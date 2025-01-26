from django.contrib import admin

# Register your models here.
from .models import Menu,Booking,Category


admin.site.register(Menu)
admin.site.register(Booking)
admin.site.register(Category)

