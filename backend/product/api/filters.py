from django_filters import rest_framework as filters
from product.models import Product

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")  # Greater than or equal
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")  # Less than or equal
    wilaya = filters.NumberFilter(field_name="commune__wilaya", lookup_expr="exact")  # Filter by wilaya ID

    class Meta:
        model = Product
        fields = ["category", "commune", "price_min", "price_max", "wilaya"]
