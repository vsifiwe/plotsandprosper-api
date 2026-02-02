"""
Custom serializers for Plots & Prosper API.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add user (name, roles) to token response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        member = getattr(user, "member", None)
        if member:
            name = f"{member.firstName} {member.lastName}".strip()
            roles = list(member.roles or [])
        else:
            name = getattr(user, "username", "") or ""
            roles = []
        data["user"] = {
            "name": name,
            "roles": roles,
        }
        return data
