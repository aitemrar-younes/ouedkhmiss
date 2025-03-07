from django.db import models
from base.models import Wilaya, Commune
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):  
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):  
        return self.name  

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductImage(models.Model):  
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')  
    image = models.ImageField(upload_to='product_images/')  
    uploaded_at = models.DateTimeField(auto_now_add=True)  
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('product', 'order')

class SavedProduct(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
