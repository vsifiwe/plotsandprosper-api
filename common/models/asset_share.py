"""
AssetShare model — member's share percentage in an asset (immutable, fixed at conversion).
"""
from django.db import models


class AssetShare(models.Model):
    """
    Member's share percentage in an asset. Fixed at conversion; no speculative revaluation.
    Immutable; corrections via Reversal.
    """

    asset = models.ForeignKey(
        "common.Asset",
        on_delete=models.PROTECT,
        related_name="asset_shares",
    )
    member = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="asset_shares",
    )
    share_percentage = models.DecimalField(
        max_digits=20, decimal_places=4
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Asset share"
        verbose_name_plural = "Asset shares"

    def __str__(self):
        return f"{self.member_id} {self.share_percentage}% of {self.asset_id}"
