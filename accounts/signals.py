from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from dispatch.models import Mechanic


@receiver(post_save, sender=User)
def create_mechanic_on_user_creation(sender, instance, created, **kwargs):
    """When a mechanic user is created with location, create a Mechanic record"""
    if created and instance.role == 'mechanic':
        # Create a Mechanic record for this user
        mechanic, _ = Mechanic.objects.get_or_create(
            name=instance.get_full_name() or instance.username,
            defaults={
                'phone': instance.phone,
                'city': instance.city,
                'latitude': instance.latitude,
                'longitude': instance.longitude,
                'is_available': True,
                'service_radius_km': 10
            }
        )


@receiver(post_save, sender=User)
def update_mechanic_location(sender, instance, created, **kwargs):
    """When a mechanic user updates their location, update the Mechanic record"""
    if instance.role == 'mechanic' and instance.latitude and instance.longitude:
        try:
            # Try to find and update Mechanic record
            mechanic = Mechanic.objects.filter(name__icontains=instance.username).first()
            if mechanic:
                mechanic.latitude = instance.latitude
                mechanic.longitude = instance.longitude
                mechanic.phone = instance.phone
                mechanic.city = instance.city
                mechanic.save()
        except Exception:
            pass

