"""
ContributionWindow model — defined time interval and rules for contributions.
"""
from django.db import models


class ContributionWindow(models.Model):
    """
    A defined time interval and rules for contributions (one per month or policy cycle).
    Immutable: no update/delete of historical windows.
    """

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    min_amount = models.DecimalField(
        max_digits=20, decimal_places=4, default=0
    )
    max_amount = models.DecimalField(
        max_digits=20, decimal_places=4, null=True, blank=True
    )
    name = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_at"]
        verbose_name = "Contribution window"
        verbose_name_plural = "Contribution windows"

    def __str__(self):
        return self.name or f"{self.start_at.date()} – {self.end_at.date()}"
