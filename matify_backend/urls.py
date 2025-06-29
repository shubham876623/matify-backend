from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('matify_api.urls')),
      path('api/auth/', include('djoser.urls')),      
       path('api/auth/', include('djoser.urls.jwt')), 
]