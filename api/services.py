from decimal import Decimal
from .models import Bid, AutoBid, Item
from django.contrib.auth.models import User


class BidService(object):

    def create_bid_by_auto(self, item: Item, value: Decimal, made_by: User, **kwargs):
        autobidding_active_items = AutoBid.objects.filter(
            item=item, is_active=True).exclude(made_by=made_by)
        autobid_obj = autobidding_active_items.first()
        if autobid_obj:
            value = value + Decimal('1')
            if value > autobid_obj.max_bid_value:
                return
            bid = Bid.objects.create(
                item=item, value=value, made_by=autobid_obj.made_by)
            return bid

    def activate_auto_bidding(self, autobid: AutoBid):
        bid = Bid.objects.filter(
            item_id=autobid.item_id).exclude(
            made_by=autobid.made_by).first()
