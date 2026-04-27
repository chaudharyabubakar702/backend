from decimal import Decimal
from math import radians, cos, sin, sqrt, atan2

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .demo_data import seed_demo_data
from .models import Mechanic, ServiceRequest, Offer, ChatMessage
from .serializers import MechanicSerializer, ServiceRequestSerializer, OfferSerializer, ChatMessageSerializer


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
    queryset = ServiceRequest.objects.select_related("assigned_mechanic").prefetch_related("offers", "messages").order_by("-created_at")
    serializer_class = ServiceRequestSerializer

    def perform_create(self, serializer):
        serializer.save()

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
        return Response(ServiceRequestSerializer(service_request).data)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_request(self, request, pk=None):
        """Allow a mechanic to accept an open request by providing mechanic id in payload.
        Payload: { "mechanic_id": <id> }
        """
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

        service_request.assigned_mechanic = mechanic
        service_request.status = ServiceRequest.ACCEPTED
        service_request.save(update_fields=["assigned_mechanic", "status"])

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

    def get_queryset(self):
        request_id = self.request.query_params.get("request")
        qs = super().get_queryset()
        return qs.filter(request_id=request_id) if request_id else qs


