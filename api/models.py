from django.db import models
from decimal import Decimal
from django.db.models import Max
from django.db import IntegrityError
from django.contrib.auth.models import User


class Item(models.Model):
    """
    Model class of auction Item
    """
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2,
                                default=Decimal('1'))

    close_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 't_item'
        ordering = ['close_datetime']

    def __str__(self):
        return self.name


class Image(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='images')
    path = models.CharField(max_length=1024)

    class Meta:
        db_table = 't_image'

    def __str__(self):
        return self.path


class Bid(models.Model):
    made_by = models.ForeignKey(User, on_delete=models.PROTECT)

    item = models.ForeignKey("Item", on_delete=models.CASCADE,
                             related_name='bids')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    value = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 't_bid'
        unique_together = ('made_by', 'value', 'item')
        ordering = ['-created_date']

    def __str__(self):
        return super().__str__()

    def save(self, *args, **kwargs):
        max_value = Bid.objects.filter(item=self.item
                                       ).aggregate(max_value=Max('value')
                                                   ).get('max_value')
        if max_value and self.value < max_value:
            raise IntegrityError
        return super(Bid, self).save(*args, **kwargs)


class AutoBid(models.Model):
    is_active = models.BooleanField(default=True)
    max_bid_value = models.DecimalField(max_digits=12, decimal_places=2)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    made_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        db_table = 't_autobid'
        unique_together = ('made_by', 'item')
