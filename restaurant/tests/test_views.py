from restaurant.models import Booking, Menu , Category
from django.test import TestCase , Client
from django.urls import reverse


class TestHomeView(TestCase):
    def setUp(self):
        self.client =  Client()
            
    def test_home_view(self):
        response = self.client.get(reverse('home')) 
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'index.html') 




class TestAboutView(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_about_view(self):
        response = self.client.get(reverse('about')) 
        self.assertEqual(response.status_code, 200)  
        self.assertTemplateUsed(response, 'about.html') 




class TestMenuView(TestCase) :
    def setUp(self):
        self.client= Client()
        
        self.category= Category.objects.create(slug = "drin",title= "Drin") #category for menu
        self.menu = Menu.objects.create( title = "test" , price =22, featured = True, category= self.category)
        
    def test_menu_view(self):
        response= self.client.get(reverse("menu"))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,"menu.html")
        self.assertContains(response,"test")