from django.contrib import admin
from django.core.checks import messages
from django.db import models
from django.db.models import Count, fields
from django.db.models.query import QuerySet
from store.views import search
from . import models
import admin_thumbnails

#creatig custom filter and add name of this class to list filter
class ProductFilter(admin.SimpleListFilter): 
    title = 'stock'
    parameter_name = 'stock'
     
    #options that displayed under title 
    def lookups(self, request, model_admin):
        return[
            ('<50','Low')
        ]

    #implimanting filtering logic 
    def queryset(self, request,queryset:QuerySet):
        if self.value()=='<50':
            return queryset.filter(stock__lt=50)


# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = models.Product_Gallery
    extra = 1
@admin.register(models.Product_Gallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ['product']
    

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    #action = ['clear_stock']
    list_display  =['product_name','price','stock_status','modified_date','is_available']
    search_fields =['product_name'] #add lookup type for moire searching 
    list_filter   =('category','modified_date',ProductFilter,)
    autocomplete_fields =['category'] 
    prepopulated_fields={'slug':['product_name']}

    inlines = [ProductGalleryInline]
    def stock_status(self,quantity):
        if quantity.stock > 50:
            return 'Ok'
        return 'low'
    
    #defining custom action    
    #@admin.action(description='clear stock')
    #def clear_stock(self,request,queryset):
     #   updated_count = queryset.update(stock=0) 
      #  self.message_user( 
       #     request,
        #    f'{updated_count} products were successfully   updated.',
         #   messages.WARNING
        #)
  
    

@admin.register(models.Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display  =('product','variation_category','variation_value','is_active')
    list_editable =('is_active',)
    list_filter   =('product','variation_category','variation_value')


@admin.register(models.Review_Rating)
class Review_RatingAdmin(admin.ModelAdmin):
    list_display  =('product','user','subject','rating','status','update_at')


    
from django.contrib import admin
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html,urlencode

from store.views import search
from .models import Category,Product,Product_Gallery,Variation

# Register your models here.

@admin.register(Category)
class categoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display        =('category_name','products_count')
    search_fields = ['category_name']
    
    #provind link to product model 
    #@admin.display(ordering='products_count')
    def products_count(self,category):
        url =(
            reverse('admin:store_product_changelist') #reverse('admin:appname_modulenamesmallcase_pagenumber')>to get url of the given modele and its object
            #the following is for query sring 
            + '?'  
            + urlencode({
                'category__id':str(category.id)
            }) 
        )
        return format_html('<a href= "{}">{}</a>',url,category.product_count)
         
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count = Count('product')
        )



    