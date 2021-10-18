from .services import BidService
from .models import AutoBid, Bid

def auto_bid_receiver_on_bid_save(sender, instance: Bid, **kwargs):
    """
    Parameters: 
        sender: Model class
        instance: instance of Model class
        kwargs:
            # SEE(django, https://docs.djangoproject.com/en/3.2/ref/signals/#post-save,)
    """
    service = BidService()
    service.create_bid_by_auto(instance.item, instance.value, instance.made_by)


def receiver_on_autobid_save(sender, instance: AutoBid, created: bool, **kwargs):
    service = BidService()
    if created:
        pass
