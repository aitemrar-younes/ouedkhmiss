from django.urls import path
from .views import AuthViewSet, UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='resend-activation')
router.register(r'users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),

    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]