from LittleLemonAPI.models          import Cart, Order , OrderItem
from django.test                    import TestCase
from django.contrib.auth.models     import User
from restaurant.models              import Menu,Category


class test_cart(TestCase):
        
    def setUp(self):
        self.user=User.objects.create_user(username = "testuser" ,password ="password123" )
        self.category = Category.objects.create(slug='good', title='Good')
        self.item = Menu.objects.create(title='apple',price = 22 ,
                                   featured = True , category=self.category)
    
    def test_get_cart(self):
        cart=Cart.objects.create(user =self.user ,menuitem =self.item ,quantity =20 ,unit_price =12.3 ,price=2.3)
        self.assertEqual(str(cart),self.user.username)




    
class test_order(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username= "mosa", password="ABC123789" )
        self.delivery_crew = User.objects.create_user(username= "Anaconda", password="ABC123789" )

    def test_get_order(self):
        order = Order.objects.create (user = self.user , delivery_crew = self.delivery_crew , status = True)
         
         # Correct assertion: Compare with expected __str__() output
        expected_str = f"{self.user.username} assigned to {self.delivery_crew.username}"
        self.assertEqual(str(order), expected_str)

    def test_get_order_without_delivery_crew(self):
        # Create an Order instance without delivery crew
        order = Order.objects.create(user=self.user, status=True)
        
        # Correct assertion for no delivery crew
        expected_str = f"{self.user.username} (No delivery crew assigned)"
        self.assertEqual(str(order), expected_str)




    
class test_OrderItem(TestCase):
    def setUp(self):
        #for order
        self.user = User.objects.create_user(username= "mosa", password="ABC123789" )
        self.delivery_crew = User.objects.create_user(username= "Anaconda", password="ABC123789" )
        
        self.order=Order.objects.create(user= self.user, delivery_crew= self.delivery_crew, status =True ) 

        #for Menu
        self.category = Category.objects.create(slug = "drinks" , title= "Drinks")
        self.menuitem= Menu.objects.create( title = "test", price = 12.20 , featured = True , category= self.category)
        
    def test_get_menuitem(self):
        item= OrderItem.objects.create(order=self.order , menuitem= self.menuitem,quantity=290 , unit_price=22 ,price= 25)
        self.assertEqual(str(item),f"{self.order.user.username} ordered {item.quantity} x {self.menuitem.title}")