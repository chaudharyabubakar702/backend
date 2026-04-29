from decimal import Decimal
from math import radians, cos, sin, sqrt, atan2
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .demo_data import seed_demo_data
from .models import Mechanic, ServiceRequest, Offer, ChatMessage
from .serializers import MechanicSerializer, ServiceRequestSerializer, OfferSerializer, ChatMessageSerializer
from accounts.models import User
from config.firebase_config import send_push_notification

logger = logging.getLogger(__name__)

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c

class MechanicViewSet(viewsets.ModelViewSet):
    queryset = Mechanic.objects.all().order_by("name")
    serializer_class = MechanicSerializer

    def perform_update(self, serializer):
        mechanic = serializer.save()
        if getattr(self.request.user, 'role', None) == User.MECHANIC:
            if hasattr(self.request.user, 'mechanic_profile') and self.request.user.mechanic_profile != mechanic:
                old_mechanic = self.request.user.mechanic_profile
                old_mechanic.user = None
                old_mechanic.save(update_fields=["user"])
                
            if mechanic.user != self.request.user:
                mechanic.user = self.request.user
                mechanic.save(update_fields=["user"])

    def list(self, request, *args, **kwargs):
        if not Mechanic.objects.exists():
            seed_demo_data()
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def nearby(self, request):
        if not Mechanic.objects.exists():
            seed_demo_data()

        lat = float(request.query_params.get("lat", 0))
        lng = float(request.query_params.get("lng", 0))
        radius = float(request.query_params.get("radius", 10))
        items = []
        for mechanic in Mechanic.objects.filter(is_available=True, latitude__isnull=False, longitude__isnull=False):
            distance = haversine_km(lat, lng, mechanic.latitude, mechanic.longitude)
            if distance <= radius:
                data = MechanicSerializer(mechanic).data
                data["distance_km"] = round(distance, 2)
                items.append(data)
        items.sort(key=lambda x: x["distance_km"])
        return Response(items)

class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.select_related("assigned_mechanic", "customer").prefetch_related("offers", "messages").order_by("-created_at")
    serializer_class = ServiceRequestSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return qs.none()
            
        if user.role == User.ADMIN:
            return qs
            
        if user.role == User.CUSTOMER:
            return qs.filter(customer=user)
            
        if user.role == User.MECHANIC:
            from django.db.models import Q
            return qs.filter(
                Q(assigned_mechanic__user=user) | 
                Q(status__in=[ServiceRequest.OPEN, ServiceRequest.NEGOTIATING])
            )
            
        return qs.none()

    def perform_create(self, serializer):
        instance = serializer.save(customer=self.request.user)
        mechanic_users = User.objects.filter(role=User.MECHANIC, fcm_token__isnull=False)
        for user in mechanic_users:
            send_push_notification(
                token=user.fcm_token,
                title="New Service Request Nearby!",
                body=f"{instance.customer_name} needs help with a {instance.vehicle_type}: {instance.issue_type}",
                data={"type": "new_request", "request_id": str(instance.id)}
            )

    @action(detail=True, methods=["post"])
    def accept_offer(self, request, pk=None):
        service_request = self.get_object()
        offer_id = request.data.get("offer_id")
        offer = service_request.offers.get(id=offer_id)
        offer.accepted = True
        offer.save(update_fields=["accepted"])
        service_request.assigned_mechanic = offer.mechanic
        service_request.final_price = offer.amount
        service_request.status = ServiceRequest.ACCEPTED
        service_request.save(update_fields=["assigned_mechanic", "final_price", "status"])
        
        if service_request.customer and service_request.customer.fcm_token:
            send_push_notification(
                token=service_request.customer.fcm_token,
                title="Request Accepted!",
                body=f"Mechanic {offer.mechanic.name} has accepted your request.",
                data={"type": "request_accepted", "request_id": str(service_request.id)}
            )
            
        return Response(ServiceRequestSerializer(service_request).data)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_request(self, request, pk=None):
        service_request = self.get_object()
        if service_request.status != ServiceRequest.OPEN and service_request.status != ServiceRequest.NEGOTIATING:
            return Response({"detail": "Request is not open for acceptance."}, status=status.HTTP_400_BAD_REQUEST)

        mechanic_id = request.data.get("mechanic_id")
        if not mechanic_id:
            return Response({"detail": "mechanic_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mechanic = Mechanic.objects.get(id=mechanic_id)
        except Mechanic.DoesNotExist:
            return Response({"detail": "Mechanic not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the mechanic profile is linked to the current logged in user
        if getattr(request.user, 'role', None) == User.MECHANIC:
            # Unlink previous mechanic profile if switching
            if hasattr(request.user, 'mechanic_profile') and request.user.mechanic_profile != mechanic:
                old_mechanic = request.user.mechanic_profile
                old_mechanic.user = None
                old_mechanic.save(update_fields=["user"])
            
            if mechanic.user != request.user:
                mechanic.user = request.user
                mechanic.save(update_fields=["user"])

        service_request.assigned_mechanic = mechanic
        service_request.status = ServiceRequest.ACCEPTED
        service_request.save(update_fields=["assigned_mechanic", "status"])

        if service_request.customer and service_request.customer.fcm_token:
            send_push_notification(
                token=service_request.customer.fcm_token,
                title="Request Accepted!",
                body=f"Mechanic {mechanic.name} has accepted your request.",
                data={"type": "request_accepted", "request_id": str(service_request.id)}
            )

        return Response(ServiceRequestSerializer(service_request).data)

    @action(detail=True, methods=["post"])
    def confirm_payment(self, request, pk=None):
        service_request = self.get_object()
        if service_request.final_price is None:
            return Response({"detail": "No final price set yet."}, status=status.HTTP_400_BAD_REQUEST)
        commission = (service_request.final_price * Decimal("0.10")).quantize(Decimal("0.01"))
        service_request.platform_commission = commission
        service_request.status = ServiceRequest.COMPLETED
        service_request.save(update_fields=["platform_commission", "status"])
        return Response({
            "request_id": service_request.id,
            "final_price": str(service_request.final_price),
            "commission": str(commission),
            "mechanic_payout": str((service_request.final_price - commission).quantize(Decimal("0.01"))),
        })

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related("request", "mechanic").order_by("-created_at")
    serializer_class = OfferSerializer

    def get_queryset(self):
        request_id = self.request.query_params.get("request")
        qs = super().get_queryset()
        return qs.filter(request_id=request_id) if request_id else qs

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.select_related("request").order_by("created_at")
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        req = instance.request
        recipient_user = None
        
        # Logging to debug why notifications aren't sending on messages
        logger.info(f"New message from {instance.sender_name} ({instance.sender_role}) for Request #{req.id}")
        
        if instance.sender_role == 'customer':
            # Recipient is mechanic
            if req.assigned_mechanic:
                recipient_user = req.assigned_mechanic.user
                logger.info(f"Recipient is Mechanic: {req.assigned_mechanic.name}, User Found: {recipient_user}")
        else:
            # Recipient is customer
            recipient_user = req.customer
            logger.info(f"Recipient is Customer, User Found: {recipient_user}")
        
        if recipient_user and recipient_user.fcm_token:
            logger.info(f"Sending notification to {recipient_user.username} (Token: {recipient_user.fcm_token[:10]}...)")
            send_push_notification(
                token=recipient_user.fcm_token,
                title=f"New Message from {instance.sender_name}",
                body=instance.message[:100],
                data={"type": "new_message", "request_id": str(req.id)}
            )
        else:
            logger.warning(f"Could not send notification: recipient_user={recipient_user}, has_token={bool(recipient_user.fcm_token) if recipient_user else False}")

    def get_queryset(self):
        request_id = self.request.query_params.get("request")
        qs = super().get_queryset()
        if request_id:
            qs = qs.filter(request_id=request_id)
            user_role = getattr(self.request.user, 'role', None)
            if user_role:
                other_role = 'mechanic' if user_role == 'customer' else 'customer'
                qs.filter(sender_role=other_role, status=ChatMessage.SENT).update(status=ChatMessage.DELIVERED)
        return qs

    @action(detail=False, methods=["post"])
    def mark_read(self, request):
        request_id = request.data.get("request")
        user_role = getattr(request.user, 'role', None)
        if not request_id or not user_role:
            return Response({"detail": "request and user role required"}, status=status.HTTP_400_BAD_REQUEST)
        
        other_role = 'mechanic' if user_role == 'customer' else 'customer'
        ChatMessage.objects.filter(
            request_id=request_id, 
            sender_role=other_role
        ).exclude(status=ChatMessage.READ).update(status=ChatMessage.READ)
        
        return Response({"status": "messages marked as read"})
