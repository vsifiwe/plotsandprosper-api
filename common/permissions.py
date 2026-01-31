"""
RBAC permission classes for Plots & Prosper API.
Uses Member.roles: MEMBER, ADMIN, AUDITOR.
"""
from rest_framework import permissions

from .models import Member
from .models.member import MemberRole


def get_member(user):
    """Return Member for user or None if not linked."""
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "member", None)


class IsMemberReadOwnAndAggregates(permissions.BasePermission):
    """
    Member role: read own data and group aggregates only.
    No access to other members' individual data.
    """

    def has_permission(self, request, view):
        member = get_member(request.user)
        if not member:
            return False
        return MemberRole.MEMBER in (member.roles or [])

    def has_object_permission(self, request, view, obj):
        # Subclasses or views can restrict to own objects only
        return self.has_permission(request, view)


class IsAdmin(permissions.BasePermission):
    """
    Administrator role: governed data entry and reconciliation.
    Can create contributions, penalties, investments, assets, exits, buy-outs, reversals.
    Auditor role has no write access: admin and write endpoints use IsAdmin only,
    so auditor (ADMIN not in roles) gets 403 on POST/PUT/PATCH/DELETE.
    """

    def has_permission(self, request, view):
        member = get_member(request.user)
        if not member:
            return False
        return MemberRole.ADMIN in (member.roles or [])


class IsAuditorReadOnly(permissions.BasePermission):
    """
    Auditor role: read-only; no write to financial data.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            member = get_member(request.user)
            if not member:
                return False
            return MemberRole.AUDITOR in (member.roles or [])
        return False
