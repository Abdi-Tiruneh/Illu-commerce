from pickle import TRUE
from django.shortcuts import render
from store.models import Product,Review_Rating
from orders.models import Order_Product
from django.views.generic import TemplateView,ListView,DetailView

def home(request):
    reviews = None
    products = Product.objects.filter(is_available = True, ordered_product__is_ordered = True).distinct().order_by('-created_date')
    for product in products:
        reviews = Review_Rating.objects.filter(product_id=product.id, status=True)
    context ={
        'products': products,
        'reviews': reviews
    }

    return render(request, 'home.html',context)

# class based view practice

# class HomeView(ListView):
#     model = Product
#     queryset = Product.objects.filter(is_available = True)
#     context_object_name = 'products'
#     template_name = 'home.html'
    


 