"""
common/admin.py
"""

from django.contrib import admin

from .models import (
    Asset,
    AssetShare,
    Contribution,
    ContributionWindow,
    HoldingShare,
    Investment,
    Member,
    Penalty,
    Reversal,
)


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


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    """Investment — immutable."""

    list_display = ["id", "recorded_at", "unit_value", "total_units", "created_at"]
    list_filter = ["recorded_at"]
    readonly_fields = ["created_at"]
    ordering = ["-recorded_at"]


@admin.register(HoldingShare)
class HoldingShareAdmin(admin.ModelAdmin):
    """Holding share — immutable."""

    list_display = ["investment", "member", "units", "created_at"]
    list_filter = ["investment"]
    search_fields = ["member__email"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    raw_id_fields = ["investment", "member"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Asset — immutable."""

    list_display = [
        "name",
        "recorded_purchase_value",
        "conversion_at",
        "source_investment",
        "created_at",
    ]
    list_filter = ["conversion_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]
    ordering = ["-conversion_at"]
    raw_id_fields = ["source_investment"]


@admin.register(AssetShare)
class AssetShareAdmin(admin.ModelAdmin):
    """Asset share — immutable."""

    list_display = ["asset", "member", "share_percentage", "created_at"]
    list_filter = ["asset"]
    search_fields = ["member__email"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
    raw_id_fields = ["asset", "member"]


@admin.register(Reversal)
class ReversalAdmin(admin.ModelAdmin):
    """Reversal — audit trail only."""

    list_display = ["original_record_type", "original_record_id", "reason", "created_at"]
    list_filter = ["original_record_type"]
    search_fields = ["reason"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
