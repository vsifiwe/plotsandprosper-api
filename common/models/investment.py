"""
Investment model — record that funds were invested at a specific date and value.
"""

from django.conf import settings
from django.db import models


class Investment(models.Model):
    """
    Record that funds were invested at a specific date and value.
    Immutable; corrections via Reversal.
    """

    recorded_at = models.DateField()
    unit_value = models.DecimalField(max_digits=20, decimal_places=4)
    total_units = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
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
        Investment meta
        """

        ordering = ["-recorded_at"]
        verbose_name = "Investment"
        verbose_name_plural = "Investments"

    def __str__(self):
        """
        String representation of the investment
        """
        return f"Investment {self.recorded_at} @ {self.unit_value}"
