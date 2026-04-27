from .models import ChatMessage, Mechanic, Offer, ServiceRequest


def seed_demo_data():
    mech1, _ = Mechanic.objects.get_or_create(
        name="Ali Auto Rescue",
        defaults={"phone": "0300-1111111", "city": "Lahore", "latitude": 31.5204, "longitude": 74.3587, "is_available": True, "service_radius_km": 15},
    )
    mech2, _ = Mechanic.objects.get_or_create(
        name="Karachi Bike Help",
        defaults={"phone": "0300-2222222", "city": "Karachi", "latitude": 24.8607, "longitude": 67.0011, "is_available": True, "service_radius_km": 12},
    )
    mech3, _ = Mechanic.objects.get_or_create(
        name="Islamabad Roadside Pro",
        defaults={"phone": "0300-3333333", "city": "Islamabad", "latitude": 33.6844, "longitude": 73.0479, "is_available": True, "service_radius_km": 20},
    )

    req1, _ = ServiceRequest.objects.get_or_create(
        customer_name="Ahmed Khan",
        customer_phone="0311-1234567",
        vehicle_type="car",
        issue_type="Tire burst",
        issue_description="Front left tire burst near DHA phase 5.",
        address="DHA Phase 5, Lahore",
        latitude=31.4697,
        longitude=74.4107,
        defaults={"status": ServiceRequest.OPEN},
    )
    req2, _ = ServiceRequest.objects.get_or_create(
        customer_name="Sana Ali",
        customer_phone="0321-7654321",
        vehicle_type="bike",
        issue_type="Engine problem",
        issue_description="Bike stopped working on main road.",
        address="Gulshan-e-Iqbal, Karachi",
        latitude=24.9240,
        longitude=67.1290,
        defaults={"status": ServiceRequest.NEGOTIATING, "assigned_mechanic": mech2},
    )

    Offer.objects.get_or_create(request=req1, mechanic=mech1, amount="2500.00", defaults={"message": "Can reach in 20 minutes."})
    Offer.objects.get_or_create(request=req2, mechanic=mech2, amount="1800.00", defaults={"message": "Includes labor and pickup."})
    ChatMessage.objects.get_or_create(request=req1, sender_name="Ahmed Khan", sender_role="customer", message="Please come quickly.")
    ChatMessage.objects.get_or_create(request=req1, sender_name="Ali Auto Rescue", sender_role="mechanic", message="I am 15 minutes away.")

