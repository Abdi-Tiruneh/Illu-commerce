
from django.core import validators
from django.db import models 
from django.db.models import Avg,Count
from django.db.models.fields import TextField
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from user.models import User
from django.utils.text import slugify
# Create your models here.
from django.db import models




# Create your models here.
class Category(models.Model):
    category_name = models.CharField( max_length = 50, unique = True)
    slug = models.SlugField (max_length = 50 , unique = True)
    description = models.TextField(max_length = 250, blank = True)
    cat_image = models.ImageField(upload_to = 'photos/catagories', blank = True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'catagories'
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name  =models.CharField(max_length=200,unique=True)
    slug          =models.SlugField(max_length= 200,unique=True)
    description   =models.TextField(max_length=500,unique = True)
    price         =models.IntegerField(
                   validators= [MinValueValidator(1)])
    images        =models.ImageField(upload_to ='photos/products')
    stock         =models.IntegerField()
    is_available  =models.BooleanField(default = True)
    category      =models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date  =models.DateTimeField(auto_now_add = True)
    modified_date =models.DateTimeField(auto_now =True)
   

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)


    def get_url(self):
        return reverse('product_detail',args=[self.category.slug,self.slug])

    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = Review_Rating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg


    def reviewCount(self):
        reviews = Review_Rating.objects.filter(product=self,status=True).aggregate(count=Count('rating'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


    class Meta:
        ordering = ['product_name']
        
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category ='color',is_active = True)
    def sizes(self):
            return super(VariationManager,self).filter(variation_category ='size',is_active = True)

variation_category_choice = (
       ('color','color'),
       ('size','size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    variation_category = models.CharField(max_length=100,choices = variation_category_choice)
    variation_value = models.CharField(max_length = 100)
    is_active = models.BooleanField(default = True)
    created_date = models.DateTimeField(auto_now = True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

class Review_Rating(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE , related_name='review_rating')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class Product_Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,default=None)
    image  = models.ImageField(upload_to = 'store/products', max_length = 255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'