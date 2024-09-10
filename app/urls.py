from app.views import index, callback
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("callback/", callback),
    path("", index),
]
