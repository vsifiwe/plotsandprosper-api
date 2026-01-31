"""
Reversal model — corrects or reverses a prior record; preserves audit trail.
"""
from django.conf import settings
from django.db import models


class ReversalRecordType(models.TextChoices):
    """
    Reversal record type choices
    """
    CONTRIBUTION = "contribution", "Contribution"
    PENALTY = "penalty", "Penalty"
    HOLDING_SHARE = "holding_share", "Holding share"
    ASSET_SHARE = "asset_share", "Asset share"
    EXIT_REQUEST = "exit_request", "Exit request"
    BUY_OUT = "buy_out", "Buy out"


class Reversal(models.Model):
    """
    Explicit record that corrects or reverses a prior record.
    Original record remains stored; aggregation excludes reversed records.
    """

    original_record_type = models.CharField(
        max_length=32, choices=ReversalRecordType.choices
    )
    original_record_id = models.PositiveIntegerField()
    reason = models.CharField(max_length=512, blank=True)
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
        Reversal meta
        """
        ordering = ["-created_at"]
        verbose_name = "Reversal"
        verbose_name_plural = "Reversals"

    def __str__(self):
        """
        String representation of the reversal
        """
        return f"Reversal of {self.original_record_type}:{self.original_record_id}"
