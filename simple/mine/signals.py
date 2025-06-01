import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ingredient

logger = logging.getLogger('ingredients')  # Match this to your LOGGING config

@receiver(post_save, sender=Ingredient)
def log_ingredient_creation(sender, instance, created, **kwargs):
    if created:
        user_id = getattr(instance, 'created_by_id', 'unknown')
        timestamp = getattr(instance, 'created_at', 'unknown')
        logger.info(f"Ingredient created: {instance.name} (by user ID: {user_id})")
