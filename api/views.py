from rest_framework import viewsets, mixins
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
# internals
from .models import (Item, Image, Bid, AutoBid)
from .pagiantion import CustomPagination
from .filters import (ItemFilter, AutoBidFilter)
from .serializers import (ItemSerializer,
                          ImageSerializer,
                          BidSerializer,
                          ItemDetailSerializer,
                          AutoBidSerializer,
                          AutoBidUpdateSerializer
                          )


class BaseViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    http_method_names = ['get', 'post', 'put']
    # permission_classes = (IsAuthenticated, )


class ItemViewSet(BaseViewSet):

    pagination_class = CustomPagination
    filterset_class = ItemFilter

    def get_queryset(self):
        queryset = Item.objects.all()
        if self.action == 'retrieve':
            queryset = queryset.annotate(max_bid_value=Max('bids__value'))
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer


class ImageViewSet(BaseViewSet):
    def get_queryset(self):
        queryset = Image.objects.all()
        return queryset

    def get_serializer_class(self):
        return ImageSerializer


class BidViewSet(BaseViewSet):
    def get_queryset(self):
        queryset = Bid.objects.all()
        return queryset

    def get_serializer_class(self):
        return BidSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as ie:
            return Response({'error': 'IntegrityError: your bid value must be higher than max value for this item!'},
                            status=status.HTTP_400_BAD_REQUEST)


class AutoBidViewSet(BaseViewSet):
    filterset_class = AutoBidFilter
    queryset = AutoBid.objects.all()

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'update':
            return AutoBidUpdateSerializer
        return AutoBidSerializer
