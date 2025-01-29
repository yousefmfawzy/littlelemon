from django.test import TestCase
from restaurant.models import Menu,Category,Booking


class test_Menu(TestCase):
    def setUp(self):
        self.category = Category.objects.create(slug='good', title='Good')
    
    def test_get_item(self):
        item = Menu.objects.create(title='apple',price = 22 ,
                                   featured = True , category=self.category) 
        self.assertEqual(str(item),'apple')


class test_Category(TestCase):
    def test_get_category(self):
        category=Category.objects.create(slug ="drinks" ,title = "Drinks")
        self.assertEqual(str(category),"Drinks")
       
        
class test_booking(TestCase):
    def test_get_booking(self):
        book=Booking.objects.create(first_name = "Ahmad",
                reservation_date = '2025-03-31',reservation_slot = "11")
        self.assertEqual(str(book),"Ahmad")