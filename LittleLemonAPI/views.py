from rest_framework.decorators      import api_view,  permission_classes
from rest_framework.response        import Response
from rest_framework.permissions     import IsAdminUser,AllowAny,IsAuthenticated
from django.contrib.auth.models     import Group, User
from rest_framework                 import status , filters
# from rest_framework.views           import APIView 
from rest_framework.generics        import ListAPIView,RetrieveUpdateAPIView , RetrieveUpdateDestroyAPIView
from .models                        import Order, OrderItem, Cart
from .serializers                   import MenuItemSerializer , singleMenuItemSerializer , UserSerializer
from restaurant.models              import Category , Menu , Booking
from restaurant.serializers         import Bookingserializer
from .serializers                   import CartSerializer , OrderSerializer , OrderItemSerializer,CategorySerializer
from django_filters.rest_framework  import DjangoFilterBackend
from django.shortcuts               import get_object_or_404
import json
from datetime import datetime
from django.core import serializers
from restaurant.forms import BookingForm
from django.http import Http404



class book(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = Bookingserializer
    
    def get(self, request, *args, **kwargs):
        #first_name = request.data.get("first_name")
        first_name = request.query_params.get("first_name") # Use query_params for GET requests
        if request.user.is_staff or request.user.is_superuser:
            bookings = Booking.objects.all()  # Fetch all bookings for staff or superuser
            serializer = self.serializer_class(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # For non-staff or non-superuser
        elif first_name:
            bookings = Booking.objects.filter(first_name=first_name)  # Filter by first_name
            if not bookings.exists():
                return Response(
                    {"message": f"No bookings found for first_name: {first_name}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = self.serializer_class(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Missing 'first_name' parameter
        return Response(
        {"message": "Missing 'first_name' query parameter. If you are a staff member, please authenticate."},
        status=status.HTTP_400_BAD_REQUEST )
    
    
    def post(self, request, *args, **kwargs):
        try:
            # Use DRF's request.data to get JSON data from the request body
            data = request.data
            
            # Validate data using BookingForm
            form = BookingForm(data)
            if form.is_valid():
                form.save()
                return Response({'message': 'Booking successful'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Invalid form data', 'details': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def delete (self,request):
        first_name = request.data.get("first_name")  # Use query_params for GET requests
        if not first_name:
            return Response(
                {"message": "Parameter 'first_name' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        bookings = Booking.objects.filter(first_name=first_name)
        if not bookings.exists():
                return Response(
                    {"message": f"No bookings found for first_name: {first_name}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        deleted_count = bookings.delete()[0]
        return Response(
            {"message": f"{deleted_count} booking(s) deleted successfully."},
            status=status.HTTP_200_OK,)  
      
      
    
@api_view(['GET','POST','DELETE'])
@permission_classes([AllowAny])
def categories(request):
    if request.method == 'GET':
        category_list = Category.objects.all()
        serializer = CategorySerializer(category_list, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.groups.filter(name = "manager").exists():
            serializer = CategorySerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED
                                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )
        else:
            return Response({"message":"only manager can add category"},
                            status=status.HTTP_401_UNAUTHORIZED
                            )
    
    
     # Handle DELETE request - Remove a category by its slug
    elif request.method == 'DELETE':
        if request.user.groups.filter(name="manager").exists():
            slug = request.data.get('slug')
            if not slug:
                return Response(
                    {"error": "Please provide a category slug."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                category = Category.objects.get(slug=slug)
                category.delete()
                return Response(
                    {"message": f"Category '{slug}' deleted successfully."},
                    status=status.HTTP_200_OK
                )
            except Category.DoesNotExist:
                return Response(
                    {"error": "Category not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {"message": "Only managers can delete categories."},
                status=status.HTTP_401_UNAUTHORIZED
            )

# add or remove user to specific group
@api_view(['POST','DELETE'])
@permission_classes([IsAdminUser]) 
def user2group(request,id):
    
    #check user_id
    try:
        user=User.objects.get(id=id)
    except User.DoesNotExist:
        users = [user.id for user in User.objects.all()]
        return Response({'message':f"Available user_id are : {users}       Please enter avalid Id"}, status=400)
        
    #check if user enter group_name or no
    group_name=request.data.get('group_name')
    if not group_name:
        return Response("please enter a group_name",status= 400)
    
    #check is it a valid group name
    try:
        group=Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        groups = [group.name for group in Group.objects.all()]
        return Response({'message':f"Available groups: {groups}       Please enter avalid group_name"}, status=400)
    
    #add user2group
    if request.method=="POST":
        user.groups.add(group)
        return Response({"message":f"{user} add successfully "})
    
        #remove user from group
    if request.method=="DELETE":
        user.groups.remove(group)
        return Response({"message":f"{user} remove successfully "})


@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def  delivery_crew_group(request):
    delivery_crew = User.objects.filter (groups__name= 'delivery-crew')
    serializer = UserSerializer(delivery_crew,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def  manager_group(request):
    manager = User.objects.filter (groups__name= 'manager')
    serializer = UserSerializer(manager, many=True)
    return Response(serializer.data)
#---------------------------------------------
# *menu items*
# List all menu items (No authentication required) 
# + add new item (authentication required)
class menuItem(ListAPIView):
    queryset= Menu.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes=[AllowAny]
    lookup_field='title'
    
     # Add filtering, ordering, and sorting backends
    filter_backends  = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields = ['title', 'price', 'category', 'featured']  # fields to filter on
    ordering_fields = [ 'title','price']  # fields to sort by
    
     # Allow managers to add a new item using POST
    def post (self, request):
        if  request.user.groups.filter(name='manager').exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Only managers can create items."}, status=status.HTTP_403_FORBIDDEN)
            

# Retrieve and Update a single menu item by its id (GET, POST, PUT,DELETE)
class singlemenuItemlistview(RetrieveUpdateAPIView):

    queryset = Menu.objects.all()
    serializer_class = singleMenuItemSerializer
    permission_classes = [AllowAny]
   
     # This method ensures you are getting the MenuItem based on the 'id' in the URL 
    def get_object(self):
        id = self.kwargs.get("id")
        return (Menu.objects.get(id=id))

# Override PUT to handle update logic for 'manager' group
    def update(self, request, *args, **kwargs):
        if  request.user.groups.filter(name='manager').exists():
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            # Validate and update the data
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response({"detail": "Only managers can create items."}, status=status.HTTP_403_FORBIDDEN)
    
    
    # Override DELETE to handle update logic for 'manager' group
    def delete(self, request, *args, **kwargs):
        try:
            # Check if the user belongs to the 'manager' group
            if request.user.groups.filter(name='manager').exists():
                instance = self.get_object()  # Fetch the object to delete
                instance_title = instance.title
                instance.delete()  # Delete the object
                return Response(
                    {"message": f"Menu item '{instance_title}' deleted successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Only managers can delete items."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Menu.DoesNotExist:
            return Response(
                {"error": "The requested menu item does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#---------------------------------------------------------
# *cart*
#use to view items, added to cart and flush cart when order done

# use to add item to cart by user.id and item.id
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request,menu_id):
    
    try:                # Fetch the menu item by its ID
        menu_item=Menu.objects.get(id=menu_id)
    except Menu.DoesNotExist:
        return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    
        # Check if the item already exists in the cart for this user
    cart_item, created=Cart.objects.get_or_create(user=user,menuitem=menu_item)

    # If the item already exists in the cart, update the quantity
    if not created:
        cart_item.quantity += int(request.data.get('quantity', 1))
    else:
        cart_item.quantity = int(request.data.get('quantity',1))
        cart_item.unit_price= menu_item.price
        cart_item.price= cart_item.unit_price * cart_item.quantity
    
    cart_item.save()
    return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)
    


# use to view items in the cart by user token 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user.id)
    if not cart_items.exists():
        return Response({"message": "Your cart is empty."}, status=status.HTTP_200_OK)
    else:
        return Response(CartSerializer(cart_items, many=True).data, status=status.HTTP_200_OK)



# use to delte item from cart by user.id and item.id
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def flush_cart (request):
    cart_items=Cart.objects.filter(user=request.user)
    cart_items.delete()
    return Response({"message": "succesfilly, Now Your cart is empty."}, status=status.HTTP_200_OK)
    

#---------------------------------------------------------

#place order 
# We’ll create separate views for customers, delivery crew, and managers. 
# in 2 class (orders - orders/{OrderId})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders(request):
    user =request.user
    if request.method == 'POST':
        
        #for manager
        if user.groups.filter(name='manager').exists():
            return Response({'message':'Manager are not allow to make order '})
            
            #for delivery-crew
        elif user.groups.filter(name='delivery-crew').exists():
            return Response({'message':'delivery-crew are not allow to make order '})
        
        else :        #for customers
            cart_items=Cart.objects.filter(user_id=user.id)
            if not cart_items:
                return Response({"error": "your Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
            order = Order.objects.create(user=user, status=0)
                
                # Transfer cart items to order items
                
            total_price = 0
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price = item.price * item.quantity
                )
                item_price = item.price * item.quantity
                total_price += item_price
            
            
            cart_items.delete()
            return Response(
                {
                    "message": "Your order is received.",
                    "order": OrderSerializer(order).data,
                    "Total Price":total_price,
                },
                status=status.HTTP_201_CREATED
                )


    if request.method == 'GET':

                #for manager
            if user.groups.filter(name='manager').exists():
                
                if not Order:
                    return Response({"message": "there is no order"}, status=status.HTTP_200_OK)
                else:
                    all_orders = Order.objects.all()
                    serializer = OrderSerializer(all_orders , many=True)
                    return Response (serializer.data , status=status.HTTP_200_OK)
                
                
                
            elif user.groups.filter(name='delivery-crew').exists():
                # Delivery crew: View assigned orders
                assigned_orders = Order.objects.filter(delivery_crew=user)
                if not assigned_orders.exists():
                    return Response({"message": "No orders assigned to you."}, status=status.HTTP_200_OK)
                delivery_serializer = OrderSerializer(assigned_orders, many=True)
                return Response(delivery_serializer.data, status=status.HTTP_200_OK)
                
                
            
            else:   #for customers
                customer_orders = Order.objects.filter(user=user)
                if not customer_orders.exists():
                    return Response({"message": "You have no orders."}, status=status.HTTP_200_OK)
                Customer_serializer = OrderSerializer(customer_orders , many=True)
                return Response (Customer_serializer.data , status=status.HTTP_200_OK)
            

class manage_order(RetrieveUpdateAPIView):
    permission_classes= [IsAuthenticated]
    

    def patch(self,request,order_id):        
        order = get_object_or_404(Order, id=order_id)         # Fetch the order or return 404 if not found
        user = request.user
             
             # Check if the user is a manager to assign delivery-crew to order
        if user.groups.filter(name='manager').exists():
            delivery_crew_id = request.data.get('delivery_crew_id') # Get the delivery crew name from the request
            if not delivery_crew_id:
                return Response({'error': 'Please provide a delivery_crew_id.'}, status=status.HTTP_400_BAD_REQUEST)
            delivery_crew = get_object_or_404(User, id=delivery_crew_id, groups__name='delivery-crew')
            order.delivery_crew = delivery_crew
            order.save()
            return Response({'message': f'Order assigned to {delivery_crew.username}.'}, status=status.HTTP_200_OK)
           
        if user.groups.filter(name='delivery-crew').exists():
            order_status= request.data.get('order_status')
            if  order_status is None:   # Explicitly check for None
                return Response({'error': 'Please provide a valid order_status (0 or 1).'}, status=status.HTTP_400_BAD_REQUEST)
            #delivery_id = user.id   #get delivery id
             # Ensure that the logged-in user is the assigned delivery crew for the order
            if order.delivery_crew != user:
                return Response({'error': 'You are not assigned to this order.'}, status=status.HTTP_403_FORBIDDEN)

            try:
                order.status = int(order_status)
                order.save()
                return Response({"message":f"order_status updated successfully to {order.status} for order ID {order.id}"})
            except ValueError: 
                return Response({'error': 'Order status must be a valid integer (0 or 1).'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message":"patch for delivery_crew to update order_status, and for managers to assign delivery to orders "})       
        
           
    def delete(self, request, order_id):
        # Fetch the order or return 404 if not found 
        try:
            order = get_object_or_404(Order, id=order_id)
        except Http404:
            return Response(
                {"error": f"Order with ID {order_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        item_id = request.data.get("item_id") 
        
        # Delete entire order 
        if not item_id: 
            # Check if the user is a manager 
            if request.user.groups.filter(name='manager').exists(): 
                order.delete()    
                return Response({"message": f"Order {order_id} deleted successfully"}) 
            else: 
                return Response(
                    {"message": "Only managers can delete orders"},
                    status=status.HTTP_403_FORBIDDEN
                ) 
        else: 
            # Remove specific item from order
            if order.user == request.user: 
                remove_item = OrderItem.objects.filter(order=order, menuitem_id=item_id).first() 
                
                if not remove_item: 
                    return Response( 
                        {"error": f"OrderItem with menuitem ID {item_id} does not exist in Order {order_id}."}, 
                        status=status.HTTP_404_NOT_FOUND, 
                    ) 
                
                # Delete the item 
                remove_item.delete() 
                return Response({
                    "message": f"Item {item_id} successfully removed from Order {order_id}"
                }) 
            else: 
                return Response(
                    {"message": "This is not your order"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            
              
    def get(self, request , order_id):
        user = request.user
        order = get_object_or_404(Order , id=order_id)
        order_serializer = OrderSerializer(order).data

        if  user.groups.filter(name='manager') :
            return Response (order_serializer)
        elif  user.groups.filter(name='delivery-crew') :
            if user == order.delivery_crew:
                return Response (order_serializer)
            else:
                return Response({"message":"This is not your order"},status=status.HTTP_400_BAD_REQUEST)
        else:
            if user == order.user:
                return Response (order_serializer)
            else:
                return Response({"message":"This is not your order"},status=status.HTTP_400_BAD_REQUEST)
            
    
            
    def put(self, request, order_id):
        try:
            user = request.user
            # Fetch the order
            order = get_object_or_404(Order, id=order_id)

            # Ensure the order belongs to the user
            if order.user != user:
                return Response({"error": "You do not have permission to modify this order."}, status=status.HTTP_403_FORBIDDEN)

            # Check if the order is assigned to a delivery crew
            if order.delivery_crew:
                return Response({"error": "You cannot modify an order assigned to a delivery crew."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch item IDs from the request
            old_menuitem_id = request.data.get("old_item_id")
            new_item_id = request.data.get("new_item_id")
            quantity = request.data.get("quantity", 1)  # Default to 1 if not specified

            # Validate input
            if not old_menuitem_id or not new_item_id:
                return Response(
                    {"error": "Both old_item_id and new_item_id must be provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ensure both IDs are integers
            try:
                old_menuitem_id = int(old_menuitem_id)
                new_item_id = int(new_item_id)
                quantity = int(quantity)
            except ValueError:
                return Response({"error": "Invalid item IDs or quantity. They must be integers."}, status=status.HTTP_400_BAD_REQUEST)

            # Get the old item
            old_item = OrderItem.objects.filter(order=order, menuitem_id=old_menuitem_id).first()
            if not old_item:
                return Response(
                    {"error": f"OrderItem with menuitem ID {old_menuitem_id} does not exist in Order {order_id}."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Fetch the new menu item
            new_menu_item = get_object_or_404(Menu, id=new_item_id)

            # Delete the old item
            old_item.delete()

            # Add the new item to the order
            new_item = OrderItem.objects.create(
                order=order,
                menuitem=new_menu_item,
                quantity=quantity,
                unit_price=new_menu_item.price,
                price=new_menu_item.price * quantity,
            )

            # Recalculate the total price of the order
            total_price = sum(item.price for item in OrderItem.objects.filter(order=order))

            # Return success response
            return Response(
                {
                    "message": f"Successfully replaced item with menuitem ID {old_menuitem_id} with item {new_item_id} in the order.",
                    "new_item": {
                        "id": new_item.id,
                        "menuitem": new_menu_item.title,
                        "quantity": new_item.quantity,
                        "unit_price": str(new_menu_item.price),
                        "price": str(new_item.price),
                    },
                    "total_price": str(total_price),
                },
                status=status.HTTP_200_OK,
            )

        except Order.DoesNotExist:
            return Response({"error": f"Order with ID {order_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except OrderItem.DoesNotExist:
            return Response(
                {"error": f"OrderItem with menuitem ID {old_menuitem_id} does not exist in Order {order_id}."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Menu.DoesNotExist:
            return Response({"error": f"MenuItem with ID {new_item_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
