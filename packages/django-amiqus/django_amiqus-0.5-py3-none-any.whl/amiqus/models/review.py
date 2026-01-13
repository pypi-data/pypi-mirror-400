from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseModel
from .step import Step


class Review(BaseModel):
    """A review of a step."""

    class ReviewStatus(models.TextChoices):
        """The status of a review."""

        PENDING = ("pending", _("Pending"))
        APPROVED = ("approved", _("Approved"))
        REJECTED = ("rejected", _("Rejected"))

    status = models.CharField(
        max_length=20,
        help_text=_("The current status of the review (from API)."),
        choices=ReviewStatus.choices,
    )
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="reviews")
