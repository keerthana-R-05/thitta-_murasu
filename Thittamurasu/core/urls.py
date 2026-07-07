from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('schemes_app.urls')), # Routes the homepage to your app
]