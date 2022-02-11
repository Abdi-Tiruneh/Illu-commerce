from django.contrib import admin

from . import models

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=('cart_id','date_added',)


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active',)


