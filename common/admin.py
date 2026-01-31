"""
common/admin.py
"""

from django.contrib import admin

from .models import Contribution, ContributionWindow, Member, Penalty


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """
    Member admin
    """

    list_display = [
        "firstName",
        "lastName",
        "email",
        "phone",
        "status",
        "joinDate",
        "roles",
    ]
    list_filter = ["status", "joinDate", "roles"]
    search_fields = ["firstName", "lastName", "email", "phone"]
    readonly_fields = ["id", "createdAt", "updatedAt"]
    ordering = ["-joinDate"]
    list_per_page = 10
    list_max_show_all = 100


@admin.register(ContributionWindow)
class ContributionWindowAdmin(admin.ModelAdmin):
    """Contribution window — minimal create for data entry."""

    list_display = ["name", "start_at", "end_at", "min_amount", "max_amount"]
    list_filter = ["start_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]
    ordering = ["-start_at"]


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """Contribution — read-only or minimal create (immutable)."""

    list_display = ["member", "window", "amount", "recorded_at"]
    list_filter = ["window", "recorded_at"]
    search_fields = ["member__email", "member__firstName"]
    readonly_fields = ["created_at"]
    ordering = ["-recorded_at"]
    raw_id_fields = ["member", "window"]


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    """Penalty — read-only or minimal create (immutable)."""

    list_display = ["member", "amount", "reason", "window", "recorded_at"]
    list_filter = ["recorded_at"]
    search_fields = ["member__email", "reason"]
    readonly_fields = ["created_at"]
    ordering = ["-recorded_at"]
    raw_id_fields = ["member", "window"]
