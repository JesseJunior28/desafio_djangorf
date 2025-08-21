from rest_framework import serializers
from .models import Item

# Serializer padrão.
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["id", "nome", "preco", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Preço não pode ser negativo.")
        return value
    
# Serializer resumido para listagens
class ItemResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['codigo_item', 'nome', 'descricao', 'preco']

# Serializer para atualização, aproveitando o Serializer padrão para deixar os campos opcionais para atualização parcial
class ItemUpdateSerializer(ItemSerializer):
    descricao = serializers.CharField(required=False)
    codigo_item = serializers.CharField(required=False)
    nome = serializers.CharField(required=False)
    preco = serializers.FloatField(required=False)
    quantidade_estoque = serializers.IntegerField(required=False)

# Para garantir que o código do item seja único ao atualizar
    def validate_codigo_item(self, codigo_item):
        
        if codigo_item != self.instance.codigo_item:
            if Item.objects.filter(codigo_item=codigo_item).exists():
                raise serializers.ValidationError("Este código de item não está disponível.")
        return codigo_item
# Para garantir que a quantidade seja inteiro e não negativo.
    def validate_quantidade_estoque(self, quant):
        if quant is not None and (not isinstance(quant, int) or quant < 0):
            raise serializers.ValidationError("Valor fornecido para quantidade é inválido.")
        return quant    