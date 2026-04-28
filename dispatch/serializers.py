from rest_framework import serializers
from .models import Mechanic, ServiceRequest, Offer, ChatMessage


class MechanicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanic
        fields = "__all__"


class OfferSerializer(serializers.ModelSerializer):
    mechanic_name = serializers.CharField(source="mechanic.name", read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "request", "mechanic", "mechanic_name", "amount", "message", "accepted", "created_at"]
        read_only_fields = ["accepted", "created_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"
        read_only_fields = ["created_at"]


class ServiceRequestSerializer(serializers.ModelSerializer):
    assigned_mechanic_name = serializers.CharField(source="assigned_mechanic.name", read_only=True)
    offers = OfferSerializer(many=True, read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            "id", "customer_name", "customer_phone", "vehicle_type", "issue_type",
            "issue_description", "address", "latitude", "longitude", "status",
            "assigned_mechanic", "assigned_mechanic_name", "final_price",
            "platform_commission", "created_at", "offers", "messages",
        ]
        read_only_fields = ["status", "assigned_mechanic_name", "final_price", "platform_commission", "created_at", "offers", "messages"]
