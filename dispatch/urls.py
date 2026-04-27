from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MechanicViewSet, ServiceRequestViewSet, OfferViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r"mechanics", MechanicViewSet, basename="mechanic")
router.register(r"requests", ServiceRequestViewSet, basename="request")
router.register(r"offers", OfferViewSet, basename="offer")
router.register(r"messages", ChatMessageViewSet, basename="message")

urlpatterns = [path("", include(router.urls))]

