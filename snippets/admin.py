from django.contrib import admin

# Register your models here.
from .models import Code, Like


admin.site.register(Code)
admin.site.register(Like)
