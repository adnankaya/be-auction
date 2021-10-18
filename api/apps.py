from django.apps import AppConfig
from django.db.models.signals import post_save
from django.core.signals import request_finished

# internal

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from api.receivers import (auto_bid_receiver_on_bid_save,
                                   receiver_on_autobid_save,
                                   )
        Bid = self.get_model('Bid')
        post_save.connect(auto_bid_receiver_on_bid_save, sender=Bid)

        AutoBid = self.get_model('AutoBid')
        post_save.connect(receiver_on_autobid_save, sender=AutoBid)