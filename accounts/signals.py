from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from dispatch.models import Mechanic


@receiver(post_save, sender=User)
def create_mechanic_on_user_creation(sender, instance, created, **kwargs):
    """When a mechanic user is created with location, create a Mechanic record"""
    # Only create a Mechanic record if the user is a mechanic.
    # latitude/longitude fields were removed from User in a migration; use getattr
    # so this signal does not raise AttributeError when those attributes are absent.
    if created and instance.role == 'mechanic':
        defaults = {
            'phone': getattr(instance, 'phone', ''),
            'city': getattr(instance, 'city', ''),
            'is_available': True,
            'service_radius_km': 10
        }

        lat = getattr(instance, 'latitude', None)
        lng = getattr(instance, 'longitude', None)
        if lat is not None:
            defaults['latitude'] = lat
        if lng is not None:
            defaults['longitude'] = lng

        # Create a Mechanic record for this user; if no lat/lng provided, still create
        # with defaults but without those keys.
        mechanic, _ = Mechanic.objects.get_or_create(
            name=instance.get_full_name() or instance.username,
            defaults=defaults
        )


@receiver(post_save, sender=User)
def update_mechanic_location(sender, instance, created, **kwargs):
    """When a mechanic user updates their location, update the Mechanic record"""
    # Use getattr so absence of latitude/longitude on User does not raise errors.
    lat = getattr(instance, 'latitude', None)
    lng = getattr(instance, 'longitude', None)
    if instance.role == 'mechanic' and lat is not None and lng is not None:
        try:
            # Try to find and update Mechanic record
            mechanic = Mechanic.objects.filter(name__icontains=instance.username).first()
            if mechanic:
                mechanic.latitude = lat
                mechanic.longitude = lng
                mechanic.phone = getattr(instance, 'phone', mechanic.phone)
                mechanic.city = getattr(instance, 'city', mechanic.city)
                mechanic.save()
        except Exception:
            pass

