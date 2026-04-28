from rest_framework import serializers
from .models import User
from dispatch.models import Mechanic

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    latitude = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    longitude = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone", "city", "latitude", "longitude"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        lat_raw = validated_data.pop("latitude", None)
        lng_raw = validated_data.pop("longitude", None)
        lat = None
        lng = None
        try:
            if lat_raw and lat_raw != "": lat = float(lat_raw)
        except: pass
        try:
            if lng_raw and lng_raw != "": lng = float(lng_raw)
        except: pass
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == 'mechanic':
            Mechanic.objects.create(
                user=user,
                name=user.username,
                phone=user.phone,
                city=user.city,
                latitude=lat,
                longitude=lng
            )

        return user

class MeSerializer(serializers.ModelSerializer):
    latitude = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    longitude = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "city", "latitude", "longitude", "fcm_token"]
        read_only_fields = ["id", "username", "email", "role"]

    def update(self, instance, validated_data):
        lat_raw = validated_data.pop('latitude', None)
        lng_raw = validated_data.pop('longitude', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if instance.role == 'mechanic':
            mech, created = Mechanic.objects.get_or_create(user=instance, defaults={'name': instance.username})
            if lat_raw: mech.latitude = float(lat_raw)
            if lng_raw: mech.longitude = float(lng_raw)
            mech.phone = instance.phone
            mech.city = instance.city
            mech.save()

        return instance
