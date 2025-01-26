from django.db import models
from django.contrib.auth.models import User
from restaurant.models import Menu

 


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    menuitem =  models.ForeignKey(Menu, on_delete= models.CASCADE)
    quantity = models. SmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2,default=2)
    price = models.DecimalField(max_digits=6, decimal_places=2,default=2)

    class Meta:
        unique_together = ('menuitem', 'user')
    def __str__(self):
        return self.user.username



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="deliver_creew", null=True)
    status = models.BooleanField(db_index=True, default=0)
   
    def __str__(self):
        if self.delivery_crew:
            returned_name = f"{self.user.username} assigned to {self.delivery_crew.username}"
        else:
            returned_name = f"{self.user.username} (No delivery crew assigned)"
        return returned_name
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menuitem = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)
   

    class Meta:
        unique_together = ('order', 'menuitem')
    
    

