from rest_framework import permissions
from orders.models import Order
from catalog.models import Item

#Define acesso/manipulação de pedidos baseado no grupo:
#Cliente: apenas visualizar seus próprios pedidos; não cria ou altera pedidos de outros.
#Funcionário: pode visualizar/criar/alterar pedidos de qualquer Cliente.
#Gerência: acesso total a todos os pedidos.
class GroupsPermissionForPedidoManipulation(permissions.BasePermission):

    
    message = "Você não possui permissão para esta operação."

    def has_permission(self, request, view):
        user = request.user

        # Clientes só podem criar pedidos para si
        if user.groups.filter(name='Cliente').exists():
            # GET e POST são permitidos, mas somente para os próprios pedidos
            return True

        # Funcionário e Gerência podem criar/visualizar
        if user.groups.filter(name__in=['Funcionário', 'Gerência']).exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.groups.filter(name='Gerência').exists():
            return True

        if user.groups.filter(name='Funcionário').exists():
            # Funcionário pode manipular pedidos de Clientes
            return obj.usuario.groups.filter(name='Cliente').exists()

        if user.groups.filter(name='Cliente').exists():
            # Para o cliente só poder acessar os seus próprios pedidos
            return obj.usuario == user

        return False

# Clientes têm apenas permissão de leitura; Funcionários e Gerência podem manipular itens.
class GroupsPermissionForItemManipulation(permissions.BasePermission):
 
    message = "Essa operação não é permitida."

    def has_permission(self, request, view):
        user = request.user

        # Sempre permitir leitura
        if request.method in permissions.SAFE_METHODS:
            return True

        # Apenas Funcionário e Gerência podem criar/atualizar/excluir itens
        if user.groups.filter(name__in=['Funcionário', 'Gerência']).exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Mesmo comportamento que has_permission; leitura liberada para todos, escrita só para Funcionário/Gerência
        return self.has_permission(request, view)