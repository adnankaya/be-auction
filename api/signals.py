from django.dispatch import Signal

providing_args = [
    'is_active',
    'max_bid_value',
    'item',
    'made_by',
]

autobid_signal = Signal(providing_args=providing_args)
