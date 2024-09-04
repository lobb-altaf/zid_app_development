from django.contrib import admin

from .models import ZidUser, ZidUserStore

# Register your models here.
# admin.site.register(TokenData)
admin.site.register(ZidUser)
admin.site.register(ZidUserStore)
