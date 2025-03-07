from django.apps import AppConfig
from django.db.utils import IntegrityError


class ProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product'

    def ready(self):
        from product.models import Category  

        default_categories = [
            "Electronics & Gadgets",
            "Fashion & Apparel",
            "Vehicles & Automotive",
            "Home & Furniture",
            "Real Estate",
            "Jobs & Services",
            "Health & Beauty",
            "Sports & Outdoor",
            "Toys, Games & Hobbies",
            "Books & Education",
            "Pets & Animals",
            "Industrial & Business",
        ]

        for category in default_categories:
            try:
                Category.objects.get_or_create(name=category)
            except IntegrityError:
                pass
