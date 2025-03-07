from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WilayaViewSet

router = DefaultRouter()
router.register(r'wilayas', WilayaViewSet, basename='wilaya')


urlpatterns = [
    path('', include(router.urls)),
]