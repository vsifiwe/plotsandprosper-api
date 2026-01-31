"""
common/admin.py
"""

from django.contrib import admin

from .models import Member


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