"""
Auth views — token obtain/refresh with user info.
"""

from rest_framework_simplejwt.views import TokenObtainPairView

from common.serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Token obtain with user name and roles in response."""

    serializer_class = CustomTokenObtainPairSerializer
