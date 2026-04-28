from django.db import models
from django.conf import settings

class Mechanic(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mechanic_profile', null=True, blank=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=80, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    service_radius_km = models.FloatField(default=10)

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    OPEN = "open"
    ACCEPTED = "accepted"
    NEGOTIATING = "negotiating"
    COMPLETED = "completed"

    STATUS_CHOICES = [
        (OPEN, "Open"),
        (ACCEPTED, "Accepted"),
        (NEGOTIATING, "Negotiating"),
        (COMPLETED, "Completed"),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests', null=True, blank=True)
    customer_name = models.CharField(max_length=120)
    customer_phone = models.CharField(max_length=30, blank=True)
    vehicle_type = models.CharField(max_length=40, default="car")
    issue_type = models.CharField(max_length=120)
    issue_description = models.TextField()
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    assigned_mechanic = models.ForeignKey(Mechanic, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id} - {self.issue_type}"


class Offer(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="offers")
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE, related_name="offers")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    STATUS_CHOICES = [(SENT, "Sent"), (DELIVERED, "Delivered"), (READ, "Read")]

    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="messages")
    sender_name = models.CharField(max_length=120)
    sender_role = models.CharField(max_length=20, choices=[("customer", "Customer"), ("mechanic", "Mechanic")])
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SENT)
    created_at = models.DateTimeField(auto_now_add=True)
