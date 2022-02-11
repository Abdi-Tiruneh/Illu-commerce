

from django.test import TestCase
from store.models import Product,Category



class TestProductModel(TestCase):

  def setUp(self):
    self.category = Category.objects.create(
      category_name = 'jeans 1'
    )

    self.product = Product.objects.create(
      product_name = 'denim 1',
      description = 'good product',
      price =10,
      stock = 10,
      category = self.category
    )
  
  def test_category_slug_is_assigned_on_creation(self):
    self.assertEquals(self.product.slug, 'denim-1')