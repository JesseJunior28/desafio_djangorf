from django.contrib.auth.models import User
from pedidos.models import Pedido
from pedidos.serializers import PedidoSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from usuarios.serializers import (
    UserSerializer,
    UserSignUpSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from usuarios.permissions import GroupsPermissionsForUserManipulation
from usuarios.utils import UserGroupVerify



#ViewSet para gerenciamento de usuários.
#Funcionalidades:
#Registro de clientes
#Criação de usuários por admin
#Listagem de usuários (parcial para clientes)
#Detalhe, update, delete
#Listagem de pedidos do usuário
        
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'  # URL baseada em username
    filterset_fields = ['username', 'email']

    #Define permissões customizadas por ação.
    def get_permissions(self):

        if self.action in ['signup']:
            return [AllowAny()]
        elif self.action in ['create']:
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), GroupsPermissionsForUserManipulation()]
        return [IsAuthenticated()]
    
    #Alterna serializer dependendo da ação e grupo do usuário.
    def get_serializer_class(self):

 
        user = self.request.user
        if self.action == 'signup':
            return UserSignUpSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action in ['list', 'retrieve']:
            if UserGroupVerify.is_cliente(user):
                return UserSignUpSerializer  # dados parciais para clientes
            return UserSerializer
        return UserSerializer

    # Ações
    def list(self, request, *args, **kwargs):
        user = request.user
        if UserGroupVerify.is_cliente(user):
            queryset = User.objects.filter(username=user.username)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, username=None):
        user_obj = self.get_object()
        serializer = self.get_serializer(user_obj)
        return Response(serializer.data)

    def update(self, request, username=None, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def destroy(self, request, username=None, *args, **kwargs):
    #Remoção de usuário
        
        return super().destroy(request, *args, **kwargs)

    # Ação customizada: pedidos do usuário
    @action(detail=True, methods=['get'], url_path='pedidos')
    def pedidos(self, request, username=None):
        user_obj = self.get_object()
        pedidos = Pedido.objects.filter(usuario=user_obj)
        serializer = PedidoSerializer(pedidos, many=True, context={'request': request, 'resume_request': True})
        return Response(serializer.data)

    # Endpoint de signup (clientes)
    @action(detail=False, methods=['post'], url_path='signup', permission_classes=[AllowAny])
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
