from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.
class Booking(models.Model):
    first_name = models.CharField(max_length=200,null=False, blank=False)
    reservation_date = models.DateField()
    reservation_slot = models.SmallIntegerField(default=10)

    def clean(self):
        if not self.first_name.strip():
            raise ValidationError({'first_name': 'First Name cannot be empty.'})

    def __str__(self): 
        return self.first_name



# Create your models here
class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255 , db_index=True,unique=True)
    def __str__(self):
        return self.title



class Menu(models.Model):   
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models. BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="menu_items")

    def __str__(self):
        return self.title
    
    
