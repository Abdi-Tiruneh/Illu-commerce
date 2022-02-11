from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Payment)
admin.site.register(models.Order_Product)

class OrderProductInLin(admin.TabularInline):
    model = models.Order_Product
    readonly_fields = ['payment','user','product','quantity','product_price','is_ordered']
    extra = 0

@admin.register(models.Order)
class ProductAdmin(admin.ModelAdmin):
    list_display  =['full_name','order_number','status','updated_at','is_ordered']
    search_fields =['order_number','first_name','last_name'] #add lookup type for moire searching 
    list_filter   =('updated_at','is_ordered','order_total','status')
    list_per_page = 20
    inlines = [OrderProductInLin]