"""
HoldingShare model — member's units in an investment (immutable).
"""
from django.db import models


class HoldingShare(models.Model):
    """
    Member X has Y units of this holding at recorded value.
    Immutable; corrections via Reversal.
    """

    investment = models.ForeignKey(
        "common.Investment",
        on_delete=models.PROTECT,
        related_name="holding_shares",
    )
    member = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="holding_shares",
    )
    units = models.DecimalField(max_digits=20, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Holding share meta
        """
        ordering = ["-created_at"]
        verbose_name = "Holding share"
        verbose_name_plural = "Holding shares"

    def __str__(self):
        """
        String representation of the holding share
        """
        return f"{self.member} {self.units} units in {self.investment}"
