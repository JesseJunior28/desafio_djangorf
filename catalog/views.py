from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from itens.models import Item
from itens.serializers import ItemSerializer, ItemResumeSerializer, ItemUpdateSerializer
from usuarios.permissions import GroupsPermissionForItemManipulation


class ItemViewSet(viewsets.ModelViewSet):
    
#ViewSet para Itens do catálogo:
#GET list/detail: resumo para clientes, completo para admin
#POST/PUT/PATCH/DELETE: permitido apenas para admin
    
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, GroupsPermissionForItemManipulation]
    
    filterset_fields = ["preco"]
    search_fields = ["nome", "descricao"]
    ordering_fields = ["nome", "preco", "created_at"]
    ordering = ["nome"]

    def get_serializer_class(self):
        
#Retorna o serializer referente a ação e grupo de usuário:
#GET para clientes/usuários não staff → ItemResumeSerializer
#GET para staff → ItemSerializer
#POST/PATCH → ItemSerializer ou ItemUpdateSerializer
        
        user = self.request.user
        if self.action in ["list", "retrieve"]:
            if user.is_authenticated and not user.groups.filter(name="Cliente").exists():
                return ItemSerializer
            elif not user.is_authenticated or user.groups.filter(name="Cliente").exists():
                return ItemResumeSerializer
        elif self.action in ["create"]:
            return ItemSerializer
        elif self.action in ["partial_update", "update"]:
            return ItemUpdateSerializer
        return ItemSerializer

    def destroy(self, request, *args, **kwargs):
        
        if not request.user.is_staff:
            return Response({"detail": "Apenas staff pode deletar itens."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return Item.objects.all()