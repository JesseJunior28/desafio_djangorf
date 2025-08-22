from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, OrderItem
from orders.permissions import IsOwnerOrAdmin
from orders.serializers import OrderDetailSerializer


#ViewSet para Pedidos:
# list: listagem resumida para clientes, completa para admin
# retrieve: detalhes completos
# create: criação com validação de estoque

class OrderViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related("itenspedido__item").all()
        if user.groups.filter(name='Cliente').exists():
            qs = qs.filter(usuario=user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return PedidoCreateSerializer
        return PedidoDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'list':
            context['resume_request'] = True
        return context