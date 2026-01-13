from django.apps import AppConfig
from django.db.models.signals import post_save
from django.dispatch import receiver


class DjangoldpStripeConfig(AppConfig):
    name = 'djangoldp_stripe'
