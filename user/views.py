from decimal import Context
from django import forms
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth.decorators import login_required
from user.models import User, UserProfile
from carts.models import Cart, CartItem
from store.models import Variation
from orders.models import Order, Order_Product
from .forms import  RegistrationForm ,ProfileForm , UserForm
# for authentication
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import escape_leading_slashes, urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
import requests

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = User.objects.create_user(
                first_name=first_name,last_name=last_name ,username=username,email=email,password=password)
            user.phone_number = phone_number
            user.save()


            #user Authentications by sending email
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string(
                'accounts/account_verification_email.html',
                {
                    'user'  :user,
                    'domain':current_site,
                    'uid'   : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
            to_mail = email
            send_email = EmailMessage(mail_subject,message,to=[to_mail])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
    else:     
        form = RegistrationForm()
    context ={
        'form' : form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_items = CartItem.objects.filter(cart=cart)
                    product_variations = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variations.append(list(variation))

                    # getting the cart item from the user to the his product variation
                    cart_items = CartItem.objects.filter(user = user)
                    existing_variation_list = []
                    id = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    for product_variation in product_variations:
                        if product_variation in existing_variation_list:
                            index = existing_variation_list.index(product_variation)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        
                        else:
                            cart_items = CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request,user)
            messages.success(request,'Logged in successfuly.')

            url = request.META.get('HTTP_REFERER') # previos url where you come
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)      
            except:
                return redirect('dashboard')

        else:
            messages.error(request,'Invalid Login Credentials')
            return redirect('login')
        
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged Out Successfuly')
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulation! your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid Activation Link')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    user_profile = get_object_or_404(UserProfile, user = request.user)
    orders = Order.objects.filter(
        user_id = request.user.id,
        is_ordered = True
    ).order_by('-created_at')
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
        'user_profile': user_profile
    }

    return render(request,'accounts/dashboard.html', context)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password'
            message = render_to_string(
                'accounts/forgot_password_email.html',
                {
                    'user'  :user,
                    'domain':current_site,
                    'uid'   : urlsafe_base64_encode(force_bytes(user.pk)),
                    'token' : default_token_generator.make_token(user),
                })
            to_mail = email
            send_email = EmailMessage(mail_subject,message,to=[to_mail])
            send_email.send()
            messages.success(request,'Reset link is just sent to your email address.')
            return redirect('login')

        else:
            messages.error(request,'User with this email is doesnt exist')
            return redirect('forgot_password')

    return render(request,'accounts/forgot_password.html')

def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.info(request,'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'This link has be expired')
        return redirect('login')

def reset_password(request):
    if request.method =='POST':
        password = request.POST['create_password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            uid = request.session['uid']
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reseted successfully!')
            return redirect('login')
        else:
            messages.error(request,'Password does not match')
            return redirect('reset_password')
    return render(request,'accounts/reset_password.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user = request.user,is_ordered = True)
    context = {
        'orders':orders
    }
    return render(request, 'accounts/my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile , user = request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST,request.FILES,instance = user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request ,'Updated Successfully')
            return redirect('edit_profile')
    else:     
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance = user_profile)
    context ={
        'user_form' : user_form,
        'profile_form' : profile_form,
        'user_profile' : user_profile
    }
    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method =='POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = User.objects.get(username__exact = request.user.username)

        if new_password==confirm_password:
            password_check = user.check_password(current_password)
            if password_check:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password updated successfully!')
                auth.logout(request)
            else:
                messages.error(request,'Please Enter Correct current password')
                return redirect('change_password')
        else:
            messages.error(request,'Password does not match ')
            return redirect('change_password')

    return render(request,'accounts/change_password.html')
   
@login_required(login_url='login')
def orders_detail(request,order_number):
    order_products =Order_Product.objects.filter(order__order_number = order_number)
    order =Order.objects.get(order_number = order_number)
    sub_total = 0

    for i in order_products:
        sub_total += i.product_price * i.quantity

    context = {
        'order_products': order_products,
        'order': order,
        'sub_total' : sub_total
    }
    return render(request, 'accounts/orders_detail.html', context)