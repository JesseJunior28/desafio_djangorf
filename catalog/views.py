from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer
from .permissions import IsStaffOrReadOnly

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["price"]
    search_fields = ["name"]
    ordering_fields = ["name", "price", "created_at"]

# catalog/urls.py
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet
router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")
urlpatterns = router.urls