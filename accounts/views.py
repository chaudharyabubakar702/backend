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

    def create(self, request, *args, **kwargs):
        """Override to log validation errors so running server shows why a 400 occurred."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            # Log helpful debug info to server console
            try:
                import logging
                logger = logging.getLogger(__name__)
                logger.error("Register validation failed. data=%s errors=%s", request.data, getattr(serializer, 'errors', exc))
            except Exception:
                print("Register validation failed.", request.data, getattr(serializer, 'errors', exc))
            raise
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Ensure the serializer knows that the username field for our User model is the email
    username_field = User.USERNAME_FIELD
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


