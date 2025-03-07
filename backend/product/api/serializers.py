from rest_framework import serializers
from product.models import Category, ProductImage, Product, SavedProduct
from base.models import Commune
from django.db import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at', 'order']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=True),
        write_only=True, required=False
    )
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    
    # New Read-Only Fields
    commune_name = serializers.CharField(source="commune.name", read_only=True)
    wilaya_id = serializers.IntegerField(source="commune.wilaya.id", read_only=True)
    wilaya_name = serializers.CharField(source="commune.wilaya.name", read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'user', 'title', 'description', 'price', 'category', 'commune', 'commune_name', 'wilaya_id', 'wilaya_name', 'created_at', 'images', 'uploaded_images']
        read_only_fields = ['user', 'commune_name', 'wilaya_id', 'wilaya_name']

    def create(self, validated_data):
        """
        Override create to handle image uploads.
        """
        uploaded_images = validated_data.pop('uploaded_images', [])  # Extract images
        product = Product.objects.create(**validated_data)  # Create product
        # Get the highest existing order value for this product
        max_order = product.images.aggregate(models.Max('order'))['order__max']
        max_order = max_order + 1 if max_order is not None else 0  # Start from 0 if no images exist

        # Save each uploaded image
        for index, image in enumerate(uploaded_images):
            ProductImage.objects.create(product=product, image=image, order=max_order + index)
        
        return product

    def update(self, instance, validated_data):
        """
        Override update to allow updating fields & adding new images.
        """
        uploaded_images = validated_data.pop('uploaded_images', [])  # Extract new images
        instance = super().update(instance, validated_data)  # Update fields
        # Get the highest existing order value for this product
        max_order = instance.images.aggregate(models.Max('order'))['order__max']
        max_order = max_order + 1 if max_order is not None else 0  # Start from 0 if no images exist
        
        # If images are provided, add them to the product
        for index, image in enumerate(uploaded_images):
            ProductImage.objects.create(product=instance, image=image, order=max_order + index)
        
        return instance
    
class SavedProductSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = SavedProduct
        fields = ['id', 'user', 'product', 'product_details', 'saved_at']
        read_only_fields = ['user', 'saved_at']

    def get_product_details(self, obj):
        """Returns serialized product details."""
        return ProductSerializer(obj.product).data
