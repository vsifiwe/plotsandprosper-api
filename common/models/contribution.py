"""
Contribution model — single immutable record of a member's savings payment within a window.
"""
from django.db import models


class Contribution(models.Model):
    """
    Single immutable record of a member's savings payment within a contribution window.
    Corrections only via Reversal; no update/delete.
    """

    member = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    window = models.ForeignKey(
        "common.ContributionWindow",
        on_delete=models.PROTECT,
        related_name="contributions",
    )
    amount = models.DecimalField(max_digits=20, decimal_places=4)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name = "Contribution"
        verbose_name_plural = "Contributions"

    def __str__(self):
        return f"Contribution {self.amount} by {self.member_id} in {self.window_id}"
