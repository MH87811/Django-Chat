from django.contrib import admin
from accounts.models import *


# Register your models here.

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    pass