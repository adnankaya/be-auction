from django.db.models import Q
from django_filters.rest_framework import (
    FilterSet, CharFilter, BooleanFilter)

from .models import Item, AutoBid


class ItemFilter(FilterSet):
    # name = CharFilter(field_name='name', lookup_expr='icontains')
    # description = CharFilter(field_name='description', lookup_expr='icontains')

    query = CharFilter(method='query_by_multiple_fields',label='search')
    
    class Meta:
        model = Item
        fields = ['query']

    def query_by_multiple_fields(self, queryset, name, value):
        q = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(q)

class AutoBidFilter(FilterSet):
    class Meta:
        model = AutoBid
        fields = ['made_by','item']