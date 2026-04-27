from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .serializers import RegisterSerializer, MeSerializer


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):
        # Accept either the USERNAME_FIELD (email) or 'username' in incoming attrs.
        username_field = self.username_field
        username_value = attrs.get(username_field) or attrs.get('email') or attrs.get('username')
        password = attrs.get('password')

        if username_value is None or password is None:
            # fallback to default behavior and let parent serializer raise useful errors
            data = super().validate(attrs)
        else:
            # build a dict using the serializer's expected username field name
            auth_attrs = {username_field: username_value, 'password': password}
            data = super().validate(auth_attrs)

        # attach role to response so frontend can redirect by role
        try:
            user = getattr(self, 'user', None) or None
            if user is not None:
                data["role"] = user.role
        except Exception:
            pass
        return data


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeAPIView(APIView):
    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


