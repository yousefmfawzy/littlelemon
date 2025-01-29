# from django.contrib.auth.models  import User
from .models import Menu , Booking
from rest_framework import serializers


  
        
class Menuserializer (serializers.ModelSerializer):
    class Meta :
        model = Menu
        fields = '__all__'
        

class Bookingserializer (serializers.ModelSerializer):
    class Meta :
        model = Booking
        fields = '__all__'