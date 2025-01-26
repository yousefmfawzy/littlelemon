from django.contrib import admin
from .models import OrderItem,Order,Cart


admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
