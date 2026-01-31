"""
Penalty model — immutable record for late or out-of-bound participation (late fee).
"""
from django.db import models


class Penalty(models.Model):
    """
    Separate immutable record for late or out-of-bound 
    participation; not combined with investment-eligible savings.
    Corrections only via Reversal; no update/delete.
    """

    member = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="penalties",
    )
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    reason = models.CharField(max_length=255, blank=True)
    window = models.ForeignKey(
        "common.ContributionWindow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="penalties",
    )
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Penalty meta
        """
        ordering = ["-recorded_at"]
        verbose_name = "Penalty"
        verbose_name_plural = "Penalties"

    def __str__(self):
        """
        String representation of the penalty
        """
        return f"Penalty {self.amount} for {self.member} ({self.reason})"
