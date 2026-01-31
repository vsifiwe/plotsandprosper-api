"""
ExitRequest model — member's request to exit; queue position and status.
Immutable creation; status/fulfilled_at updated when fulfilled or cancelled.
"""

from django.db import models


class ExitRequestStatus(models.TextChoices):
    """Status of an exit request."""

    QUEUED = "queued", "Queued"
    FULFILLED = "fulfilled", "Fulfilled"
    CANCELLED = "cancelled", "Cancelled"


class ExitRequest(models.Model):
    """
    Immutable record that a member has requested early exit.
    queue_position assigned FIFO; status/fulfilled_at set when fulfilled or cancelled.
    """

    member = models.ForeignKey(
        "common.Member",
        on_delete=models.PROTECT,
        related_name="exit_requests",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    queue_position = models.PositiveIntegerField()
    status = models.CharField(
        max_length=16,
        choices=ExitRequestStatus.choices,
        default=ExitRequestStatus.QUEUED,
    )
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    amount_entitled = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["queue_position", "-requested_at"]
        verbose_name = "Exit request"
        verbose_name_plural = "Exit requests"

    def __str__(self):
        """
        String representation of the exit request
        """
        return f"Exit request {self.member} {self.status}"
