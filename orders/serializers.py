from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from orders.models import Order, OrderItem
from catalog.models import Item


# --- Serializers auxiliares ---
class OrderItemCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemReadSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_description = serializers.CharField(source="item.description", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "item_name", "item_description"]


# --- Order (Create) ---
class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "status", "items"]
        read_only_fields = ["id", "created_at", "status"]

    def validate_user(self, user):
        """Validate if the user is valid and if clients can create orders for other users."""
        request_user = self.context["request"].user
        if request_user.groups.filter(name="Client").exists() and request_user.username != user:
            raise serializers.ValidationError("This operation is not allowed for Clients.")

        try:
            return User.objects.get(username=user)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

    @transaction.atomic
    def create(self, validated_data):
        request_user = self.context["request"].user
        items_data = validated_data.pop("items")

        # Define the user for the order
        user = validated_data.get("user", request_user)

        # Create the order
        order = Order.objects.create(user=user)

        # Track items without sufficient stock
        out_of_stock_items = []

        for item_data in items_data:
            item = Item.objects.get(pk=item_data["item_id"])
            quantity = item_data["quantity"]

            if item.stock_quantity >= quantity:
                item.stock_quantity -= quantity
                item.save()
                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=quantity,
                    unit_price=item.price
                )
            else:
                out_of_stock_items.append(item.name)

        if out_of_stock_items:
            order.delete()
            raise serializers.ValidationError(
                f"Item(s) out of stock: {', '.join(out_of_stock_items)}"
            )

        return order


# --- Order (Read/Detail) ---
class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, source="items")
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "status", "items", "total"]

    def get_total(self, obj):
        return sum(item.quantity * item.unit_price for item in obj.items.all())

    def to_representation(self, instance):
        """Remove sensitive fields if the user is a Client."""
        user = self.context["request"].user
        fields = super().to_representation(instance)

        if user.groups.filter(name="Client").exists():
            fields.pop("user", None)
            fields.pop("id", None)

        if self.context.get("resume_request", False):
            fields.pop("items", None)

        return fields
