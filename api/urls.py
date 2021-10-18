from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
# internals
from .views import (ItemViewSet,ImageViewSet,BidViewSet, AutoBidViewSet)

app_name = 'api'

router = SimpleRouter()
router.register(r'items', ItemViewSet, basename='items')
router.register(r'images', ImageViewSet, basename='images')
router.register(r'bids', BidViewSet, basename='bids')
router.register(r'autobids', AutoBidViewSet, basename='autobids')


urlpatterns = [
    path('', include(router.urls)),
]
