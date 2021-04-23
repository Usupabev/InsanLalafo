from rest_framework import serializers
from rest_framework.fields import Field

from account.serializers import UserSerializer
from general.serializer import PostSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'post', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    post = CartItemSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        total = Field(source='total')
        total_cart_products = Field(source='total_cart_post')
        fields = ['id', 'user', 'post', 'total', 'total_cart_post']

