from django.contrib.auth.models import User
from orders.models import Order
from orders.serializers import OrderDetailSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from users.serializers import (
    UserSerializer,
    UserSignUpSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from users.permissions import GroupsPermissionForItemManipulation

#ViewSet para gerenciamento de usuários.
#Funcionalidades:
#Registro de clientes
#Criação de usuários por admin
#Listagem de usuários (parcial para clientes)
#Detalhe, update, delete
#Listagem de pedidos do usuário

class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    lookup_field = 'username'  # URL baseada em username
    filterset_fields = ['username', 'email']

    def get_permissions(self):
        if self.action == 'signup':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy', 'pedidos']:
            return [IsAuthenticated(), GroupsPermissionForItemManipulation()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        user = self.request.user
        if self.action == 'signup':
            return UserSignUpSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action in ['list', 'retrieve']:
            # Clientes recebem dados parciais
            if UserGroupVerify.is_cliente(user):
                return UserSignUpSerializer
            return UserSerializer
        return UserSerializer

    def get_queryset(self):
        
        #Filtrar queryset dinamicamente:
        #Clientes veem apenas seu próprio usuário
        #Funcionário/Gerência veem todos
        
        user = self.request.user
        if UserGroupVerify.is_cliente(user):
            return User.objects.filter(username=user.username)
        return super().get_queryset()

    @action(detail=True, methods=['get'], url_path='pedidos',
            permission_classes=[GroupsPermissionForItemManipulation])
    def pedidos(self, request, username=None):
        
        #Listagem de pedidos de um usuário específico.
        #Clientes só visualizam seus próprios pedidos.
        
        user_obj = self.get_object()
        pedidos = Pedido.objects.filter(usuario=user_obj)
        serializer = PedidoSerializer(pedidos, many=True, context={'request': request, 'resume_request': True})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='signup', permission_classes=[AllowAny])
    def signup(self, request):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
