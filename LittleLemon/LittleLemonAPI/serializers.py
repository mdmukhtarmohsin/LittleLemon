from rest_framework import serializers
from . import models
from django.contrib.auth.models import User, Group


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer

    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = '__all__'
