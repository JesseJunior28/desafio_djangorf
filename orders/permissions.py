from rest_framework import permissions


#Permissões:
#Usuário normal só pode acessar seus próprios pedidos
#Admin/Staff pode acessar todos
    
class IsOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.usuario == request.user