"""
Signal handlers for The Pay payment provider registration.
"""
from django.dispatch import receiver
from pretix.base.signals import register_payment_providers


@receiver(register_payment_providers, dispatch_uid="payment_thepay")
def register_payment_provider(sender, **kwargs):
    """
    Register The Pay payment provider with Pretix.
    
    This signal handler is called by Pretix to discover available
    payment providers and registers the The Pay provider.
    """
    from .payment import ThePay
    return ThePay

