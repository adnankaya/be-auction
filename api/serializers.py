from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
# internal
from .models import (Item, Image, Bid, AutoBid)


class AutoBidSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = AutoBid
        fields = ('id', 'made_by', 'item', 'is_active',
                  'max_bid_value', 'item_name')


class AutoBidUpdateSerializer(AutoBidSerializer):
    class Meta(AutoBidSerializer.Meta):
        fields = ('id', 'is_active', 'max_bid_value')

    def update(self, instance, validated_data):
        autobid = super().update(instance, validated_data)
        return autobid


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'path', 'item')


class ItemImageSerializer(ImageSerializer):
    class Meta(ImageSerializer.Meta):
        fields = ('id', 'path')


class BidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = ('id', 'made_by',
                  'item', 'value', 'created_date')

    def create(self, validated_data):
        # TODO move to services

        item = validated_data.get('item')
        made_by = validated_data.get('made_by')
        if (self._validate_bid_user(item, made_by) and
            self._check_close_datetime(item) and
                self._check_if_bid_value_gt_max_bid_amount(validated_data)):
            return super().create(validated_data)

    def _validate_bid_user(self, item, made_by):
        last_bid = item.bids.select_related('made_by').first()
        if last_bid and last_bid.made_by == made_by:
            raise serializers.ValidationError(
                "You already made a bid for this item!")

        return True

    def _check_close_datetime(self, item):
        now = datetime.now(tz=timezone.utc)
        if item.close_datetime <= now:
            raise serializers.ValidationError(
                "Bidding for this item closed! You late.")
        return True

    def _check_if_bid_value_gt_max_bid_amount(self, vd):
        autobid = AutoBid.objects.filter(item=vd.get('item'),
                                         made_by=vd.get('made_by')).first()
        if autobid and vd.get('value') >= autobid.max_bid_value:
            raise serializers.ValidationError(
                "Bid value exceeded the max amount for this item!"
            )
        return True


class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ('id', 'name', 'description',
                  'price', 'close_datetime', 'images', )


class MadeBySerializer(serializers.Serializer):
    username = serializers.CharField()


class ItemBidSerializer(BidSerializer):
    made_by = MadeBySerializer()

    class Meta(BidSerializer.Meta):
        fields = BidSerializer.Meta.fields+('created_date', )


class ItemDetailSerializer(ItemSerializer):
    bids = ItemBidSerializer(many=True)
    max_bid_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True)

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ('bids', 'max_bid_value')
