from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from itens.models import Item
from pedidos.models import Pedido, ItemPedido


# --- Serializers auxiliares ---
class ItemPedidoCreateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)


class ItemPedidoReadSerializer(serializers.ModelSerializer):
    codigo_item = serializers.CharField(source="item.codigo_item", read_only=True)
    descricao = serializers.CharField(source="item.descricao", read_only=True)

    class Meta:
        model = ItemPedido
        fields = ["id", "codigo_item", "descricao", "quantidade"]


# --- Pedido (Create) ---
class PedidoCreateSerializer(serializers.ModelSerializer):
    itens = ItemPedidoCreateSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ["id", "codigo_pedido", "usuario", "data_criacao", "itens"]
        read_only_fields = ["id", "codigo_pedido", "data_criacao"]

    def validate_usuario(self, usuario):
        """Valida se o usuário informado é válido e se clientes podem criar pedidos para outros usuários."""
        request_user = self.context["request"].user
        if request_user.groups.filter(name="Cliente").exists() and request_user.username != usuario:
            raise serializers.ValidationError("Esta operação não é permitida para Clientes.")

        try:
            return User.objects.get(username=usuario)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

    @transaction.atomic
    def create(self, validated_data):
        request_user = self.context["request"].user
        itens_data = validated_data.pop("itens")

        # Define o usuário do pedido
        user = validated_data.get("usuario", request_user)

        # Cria o pedido
        pedido = Pedido.objects.create(usuario=user)

        # Controle de erro para itens sem estoque
        itens_sem_estoque = []

        for item_data in itens_data:
            item = Item.objects.get(pk=item_data["item_id"])
            quantidade = item_data["quantidade"]

            if item.quantidade_estoque >= quantidade:
                item.quantidade_estoque -= quantidade
                item.save()
                ItemPedido.objects.create(
                    pedido=pedido,
                    item=item,
                    quantidade=quantidade
                )
            else:
                itens_sem_estoque.append(item.nome)

        if itens_sem_estoque:
            pedido.delete()
            raise serializers.ValidationError(
                f"Item(s) sem estoque suficiente: {', '.join(itens_sem_estoque)}"
            )

        return pedido


# --- Pedido (Read/Detail) ---
class PedidoDetailSerializer(serializers.ModelSerializer):
    itens = ItemPedidoReadSerializer(many=True, source="itenspedido")
    total = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ["id", "codigo_pedido", "usuario", "data_criacao", "itens", "total"]

    def get_total(self, obj):
        return sum(ip.quantidade * ip.item.preco for ip in obj.itenspedido.all())

    def to_representation(self, instance):
        """Remove campos sensíveis caso o usuário seja Cliente."""
        user = self.context["request"].user
        fields = super().to_representation(instance)

        if user.groups.filter(name="Cliente").exists():
            fields.pop("usuario", None)
            fields.pop("id", None)

        if self.context.get("resume_request", False):
            fields.pop("itens", None)

        return fields
