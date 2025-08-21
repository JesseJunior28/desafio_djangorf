# catalog/urls.py
from rest_framework.routers import DefaultRouter

# quando criar o ViewSet, descomente e registre:
# from .views import ItemViewSet
router = DefaultRouter()
# router.register(r"items", ItemViewSet, basename="item")

urlpatterns = router.urls