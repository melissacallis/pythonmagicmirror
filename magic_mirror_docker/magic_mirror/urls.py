from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),  # Admin site
    path('', include('mirror.urls')),
    # Route root URL to the 'mirror' app
]
