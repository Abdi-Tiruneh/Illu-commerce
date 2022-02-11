import re
from turtle import home
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from orders.forms import OrderForm
from .models import Order, Payment,Order_Product
from carts.models import CartItem
import datetime
from store.models import Product
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import json


  

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],

    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    order.order_number
    
    # moving cartitems to order product table
    cart_items = CartItem.objects.filter(user = request.user)
    for item in cart_items:
        ordered_product = Order_Product()
        ordered_product.order_id = order.id
        ordered_product.payment = payment
        ordered_product.user_id = request.user.id
        ordered_product.product_id = item.product.id
        ordered_product.quantity = item.quantity
        ordered_product.product_price = item.product.price
        ordered_product.total_for_product = item.quantity*item.product.price
        ordered_product.is_ordered = True
        ordered_product.save()

        cart_items = CartItem.objects.get(id=item.id)
        product_variation = cart_items.variations.all()
        ordered_product = Order_Product.objects.get(id=ordered_product.id)
        ordered_product.variation.set(product_variation)
        ordered_product.save()

        product = Product.objects.get(id = item.product_id)
        product.stock -=item.quantity
        product.save()
   
    CartItem.objects.filter(user = request.user).delete()
    # send order recived email to customer
    mail_subject = 'Your order is recieved. thanks for shooping with us'
    message = render_to_string(
        'orders/thankyou_email.html',
        {
            'order' : order
        })
    to_mail = order.email
    send_email = EmailMessage(mail_subject,message,to=[to_mail])
    send_email.send()

    data = {
        'order_number':order.order_number,
        'transID': payment.payment_id
    }
    request.session['order_number'] = order.order_number
    request.session['transID'] = payment.payment_id
    return JsonResponse(data)
    

def place_order(request,total =0 ,quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_items_count = cart_items.count()
    if cart_items_count == 0:
        return redirect('store')    
    
    tax = 0
    grand_total = 0
    try:       
        cart_items = CartItem.objects.filter(user = request.user,is_active = True)
        for cart_item in cart_items:
            total +=(cart_item.product.price*cart_item.quantity)
            quantity +=cart_item.quantity
        tax = (2*total)/100
        grand_total = total + tax
    except:
        print("from except")
   

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone_number = form.cleaned_data['phone_number']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']  
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.region = form.cleaned_data['region']
            order.city = form.cleaned_data['city']
            order.order_note = form.cleaned_data['order_note']
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()
            #Generating order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d =datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            order_object = Order.objects.get(user = current_user, is_ordered=False,order_number=order_number)
            context ={
                'order':order_object,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
                'order_number':order_number, # for payment
            }
            request.session['order_number'] = order_number
            return render(request, 'orders/payments.html',context)
        else:
            return redirect('checkout')

    else:     
        form = OrderForm()
    context ={
        'form' : form,
    }
    return render(request,'store/checkout.html',context)

def order_complete(request):
    order_number = request.session['order_number']
    transID = request.session['transID']

    try:
        order = Order.objects.get(order_number = order_number,is_ordered = True)
        ordered_product =Order_Product.objects.filter(order_id =order.id)
        payment = Payment.objects.get(payment_id = transID)

        sub_total = 0
        for i in ordered_product:
            sub_total +=i.quantity*i.product_price
        context ={ 
                    'order':order,
                    'ordered_product':ordered_product,
                    'order_number': order.order_number,
                    'payment' : payment,
                    'transID' : payment.payment_id,
                    'sub_total':sub_total
            }
        return render(request,'orders/order_complete.html', context)
    except(Order.DoesNotExist):
        return redirect('home')