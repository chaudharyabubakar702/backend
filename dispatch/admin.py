from django.contrib import admin
from .models import Mechanic, ServiceRequest, Offer, ChatMessage

admin.site.register(Mechanic)
admin.site.register(ServiceRequest)
admin.site.register(Offer)
admin.site.register(ChatMessage)

