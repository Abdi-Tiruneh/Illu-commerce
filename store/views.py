from cmath import pi
import re
from django.contrib.auth.models import User
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import DetailView
from django.contrib import messages

from orders.models import Order_Product
from .models import Product, Product_Gallery, Review_Rating
from store.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from .forms import ReviewRatingForm
import requests


# Create your views here.
def store(request,category_slug = None):
    categories = None
    products = None

    url = request.META.get('HTTP_REFERER') # previos url where you come
    try:
        print("before query")
        requests.utils.urlparse
        query = requests.utils.urlparse(url).query
        print("afrt query")
        params = dict(x.split('=') for x in query.split('&'))
        if 'category' in params:
            next_page = params['category']
    except:
        pass

    if request.method == 'POST':
        max = request.POST['max']
        min = request.POST['min']
        if category_slug !=None:
            categories= get_object_or_404(Category,slug=category_slug)
            products = Product.objects.filter(
                category=categories, is_available = True ,price__gte=min, price__lte=max).order_by('-created_date')
            paginator = Paginator(products,6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
 
        else:
            products = Product.objects.all().filter(
                is_available = True,price__gte=min, price__lte=max).order_by('-created_date')
            paginator = Paginator(products,6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
        
    else:
        if category_slug !=None:
            categories= get_object_or_404(Category,slug=category_slug)
            products = Product.objects.filter(category=categories, is_available = True).order_by('-created_date')
            paginator = Paginator(products,6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

        else:
            print('last else')
            products = Product.objects.all().filter(
                is_available = True).order_by('-created_date')
            paginator = Paginator(products,6)
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()

    context ={'products': paged_products,
              'product_count':product_count,
              'paginator' : paginator,
    }
    return render(request,'store/store.html',context)

def product_detail(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug,slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product).exists() 
    except Exception as e:
        raise e
        
    ordered_product = None
    try:
        if request.user.is_authenticated:
            ordered_product = Order_Product.objects.filter(user = request.user, product_id=single_product.id).exists()
    except Order_Product.DoesNotExist:
        ordered_product = None
  
    reviews = Review_Rating.objects.filter(product_id=single_product.id, status=True)
    product_gallery = Product_Gallery.objects.filter(product_id=single_product.id)



    context = {
            'single_product':single_product,
            'in_cart':in_cart,
            'ordered_product': ordered_product,
            'reviews': reviews,
            'product_gallery':product_gallery
    }
    return render (request,'store/product_detail.html',context)


def search(request):
    products = 0
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
            product_count = products.count()
        else:
            return redirect('store')
    context ={'products': products,
              'product_count':product_count,
    }
    return render (request,'store/store.html',context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER') # to get current ulr
    if request.method == 'POST':
        try:
            reviews = Review_Rating.objects.get(
                user__id = request.user.id,
                product__id =product_id)
            form = ReviewRatingForm(request.POST, instance=reviews)
            # we pass instance to update existing object
            form.save()
            messages.success(request ,'Updated Successfully')
            return redirect(url)
        except Review_Rating.DoesNotExist:
            form = ReviewRatingForm(request.POST)
            if form.is_valid():
                data = Review_Rating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success (request ,'Created Successfully')
                return redirect(url)
    else:
        form = ReviewRatingForm()
              
    context ={
        'form' : form,
    }
    return render(request,'store/product_detail.html',context)
                
    



  