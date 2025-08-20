from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderCreateSerializer, OrderDetailSerializer
from .permissions import IsOwnerOrAdmin

class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items__item").all()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderDetailSerializer

# orders/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
urlpatterns = router.urls