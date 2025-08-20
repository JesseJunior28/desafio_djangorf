from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from catalog.models import Item

class OrderItemCreate(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreate(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "items"]
        read_only_fields = ["id", "created_at"]

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data.pop("items")
        order = Order.objects.create(user=user)
        for it in items_data:
            item = Item.objects.get(pk=it["item_id"])
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=it["quantity"],
                unit_price=item.price,
            )
        return order

class OrderItemRead(serializers.ModelSerializer):
    name = serializers.CharField(source="item.name", read_only=True)
    class Meta:
        model = OrderItem
        fields = ["item", "name", "quantity", "unit_price"]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemRead(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "items", "total"]

    def get_total(self, obj):
        return sum([oi.quantity * oi.unit_price for oi in obj.items.all()])