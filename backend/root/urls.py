from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('base.api.urls')),
    path('api/v1/', include('product.api.urls')),
    path('api/v1/', include('account.api.urls')),



]

if settings.DEBUG:  # Only serve media in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)