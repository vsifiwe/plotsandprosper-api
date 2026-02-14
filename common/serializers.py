"""
Custom serializers for Plots & Prosper API.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add user (name, role) to token response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        member = getattr(user, "member", None)
        if member:
            name = f"{member.firstName} {member.lastName}".strip()
            roles = list(member.roles or [])
            # DB returns strings; normalize in case of enum
            roles = [
                r if isinstance(r, str) else getattr(r, "value", r)
                for r in roles
            ]
        else:
            name = getattr(user, "username", "") or ""
            roles = []

        # Prefer highest-privilege role: ADMIN > AUDITOR > MEMBER
        role_priority = ("ADMIN", "AUDITOR", "MEMBER")
        role = next((r for r in role_priority if r in roles), roles[0] if roles else "")
        data["user"] = {
            "name": name,
            "role": role,
        }
        return data
