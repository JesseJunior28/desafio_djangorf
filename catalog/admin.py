from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'nome', 'preco', 'created_at']
    search_fields = ['nome', 'descricao']
