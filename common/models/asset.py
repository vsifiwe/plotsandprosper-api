"""
Asset model — long-term asset (e.g. property) created from holdings; ownership fixed at conversion.
"""

from django.conf import settings
from django.db import models


class Asset(models.Model):
    """
    Long-term asset created from holdings; ownership fixed at conversion.
    Immutable; corrections via Reversal.
    """

    name = models.CharField(max_length=255)
    recorded_purchase_value = models.DecimalField(max_digits=20, decimal_places=4)
    conversion_at = models.DateField()
    source_investment = models.ForeignKey(
        "common.Investment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="converted_assets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        """
        Asset meta
        """

        ordering = ["-conversion_at"]
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        return f"{self.name} ({self.conversion_at})"
