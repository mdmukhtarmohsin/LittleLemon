from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
import datetime
from . import models
from . import serializers
from rest_framework import filters
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Create your views here.


class MenuItemView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle]
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['title', 'price']
    ordering_fields = ['price', 'title']

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return [IsAuthenticated()]

        return [IsAdminUser()]


class CategoryView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAdminUser]
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['title']


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle]
    queryset = models.MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return [IsAuthenticated()]

        return [IsAdminUser()]


class Managers_view(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(groups=1)
    serializer_class = serializers.StaffSerializer

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='manager')
            managers.user_set.add(user)
            user.is_staff = True
            user.save()
            return Response({'message': 'Manager added'})

        return Response({'Error': 'Bad Request'}, status.HTTP_400_BAD_REQUEST)


class SingleManagers_view(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(groups=1)
    serializer_class = serializers.StaffSerializer

    def delete(self, request, pk):
        if pk:
            user = User.objects.get(id=pk)
            managers = Group.objects.get(name='manager')
            managers.user_set.remove(user)
            user.is_staff = False
            user.save()
            return Response({'message': 'Manager Removed'})

        return Response({'Error': 'Bad Request'}, status.HTTP_400_BAD_REQUEST)


class Delivery_crew_view(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(groups=2)
    serializer_class = serializers.StaffSerializer

    def post(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='delivery-crew')
            delivery_crew.user_set.add(user)
            return Response({'message': 'Delivery-crew added'})

        return Response({'Error': 'Bad Request'}, status.HTTP_400_BAD_REQUEST)


class SingleDelivery_crew_view(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(groups=2)
    serializer_class = serializers.StaffSerializer

    def delete(self, request, pk):
        if pk:
            user = User.objects.get(id=pk)
            delivery_crew = Group.objects.get(name='delivery-crew')
            delivery_crew.user_set.remove(user)
            return Response({'message': 'Delivery-crew Removed'})

        return Response({'Error': 'Bad Request'}, status.HTTP_400_BAD_REQUEST)


class Cart_view(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = models.Cart.objects.filter(user=request.user.id)
        serializer = serializers.CartSerializer(query, many=True)
        return Response(serializer.data)

    def delete(self, request):
        id = request.user.id
        cart = models.Cart.objects.filter(user=id)
        cart.delete()
        return Response({'message': 'Cart Cleared'})

    def post(self, request):
        quantity = request.data['quantity']
        menuitem = request.data['menuitem']
        query = models.Cart()
        itemquery = models.MenuItem.objects.get(title=menuitem)
        query.quantity = quantity
        query.menuitem = models.MenuItem.objects.get(title=menuitem)
        query.user = request.user
        query.unit_price = itemquery.price
        query.price = int(quantity)*int(query.unit_price)
        query.save()
        serializer = serializers.CartSerializer(query)
        return Response(serializer.data)


class Order_view(APIView):
    throttle_classes = [UserRateThrottle]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deliverycrew = User.objects.filter(groups=2)
        if (request.user.is_staff == True):
            query = models.Order.objects.all()
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)
        elif request.user in deliverycrew:
            query = models.Order.objects.filter(delivery_crew=request.user.id)
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)
        else:
            query = models.Order.objects.filter(user=request.user.id)
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)

    def post(self, request):
        userorder = models.Order()
        totalprice = 0
        userorder.user = request.user
        userorder.total = totalprice
        userorder.date = datetime.date.today()
        userorder.save()
        cart = models.Cart.objects.filter(user=request.user.id)
        for i in cart:
            orderitem = models.OrderItem()
            orderitem.order = userorder
            orderitem.menuitem = i.menuitem
            orderitem.quanity = i.quantity
            orderitem.unit_price = i.unit_price
            orderitem.price = i.price
            totalprice = totalprice + i.price
            orderitem.save()
            serializer = serializers.OrderItemSerializer(orderitem)
        cart.delete()
        userorder.total = totalprice
        userorder.save()
        serializer = serializers.OrderSerializer(userorder)
        return Response(serializer.data)


class SingleOrder_view(APIView):
    throttle_classes = [UserRateThrottle]

    def get(self, request, pk):
        deliverycrew = User.objects.filter(groups=2)
        if (request.user.is_staff == True):
            query = models.Order.objects.filter(id=pk)
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)
        elif request.user in deliverycrew:
            query = models.Order.objects.filter(id=pk)
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)
        else:
            query = models.Order.objects.filter(id=pk, user=request.user.id)
            serializer = serializers.OrderSerializer(query, many=True)
            return Response(serializer.data)

    def patch(self, request, pk):
        deliverycrew = User.objects.filter(groups=2)
        if (request.user.is_staff == True):
            query = models.Order.objects.get(id=pk)
            delivery = request.data['delivery_crew']
            delquery = User.objects.get(username=delivery)
            if delquery in deliverycrew:
                query.delivery_crew = delquery
                query.save()
                serializer = serializers.OrderSerializer(query)
                return Response(serializer.data)
            else:
                return Response({'Error': 'Bad Request'}, status.HTTP_400_BAD_REQUEST)

        elif request.user in deliverycrew:
            status_data = request.data['status']
            query = models.Order.objects.get(id=pk)
            query.status = status_data
            query.save()
            serializer = serializers.OrderSerializer(query)
            return Response(serializer.data)
        else:
            return Response({'Error': 'Not authorized'}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if (request.user.is_staff == True):
            query = models.Order.objects.get(id=pk)
            query.delete()
            return Response({'message': 'order deleted'})

        else:
            return Response({'message': 'Not Authorized'})
