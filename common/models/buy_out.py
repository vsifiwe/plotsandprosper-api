"""
BuyOut model — immutable record of ownership transfer at nominal valuation.
"""

from django.conf import settings
from django.db import models


class BuyOut(models.Model):
    """
    Immutable record of ownership transfer using nominal valuation.
    seller_id required; buyer_id nullable if group buys.
    """

    seller = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="buy_outs_as_seller",
    )
    buyer = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="buy_outs_as_buyer",
    )
    nominal_valuation = models.DecimalField(max_digits=20, decimal_places=4)
    valuation_inputs = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField()
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
        Buy out meta
        """

        ordering = ["-recorded_at"]
        verbose_name = "Buy out"
        verbose_name_plural = "Buy outs"

    def __str__(self):
        """
        String representation of the buy out
        """
        return f"Buy out {self.seller} @ {self.nominal_valuation}"
