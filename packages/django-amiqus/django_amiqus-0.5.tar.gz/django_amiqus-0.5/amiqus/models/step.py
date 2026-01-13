from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from .check import Check
from .form import Form
from .record import Record


class Step(models.Model):
    """
    A step in a record.

    These can be of type Check or Form and should be associated with one or more
    Reviews once they have been completed.
    """

    id = models.AutoField(primary_key=True)

    amiqus_id = models.CharField(
        "Amiqus ID",
        max_length=40,
        help_text=_(
            "The id returned from the Amiqus API. These should be unique on the record."
        ),
        null=True,
    )

    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="steps")
    amiqus_check = models.OneToOneField(
        Check, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )
    form = models.OneToOneField(
        Form, on_delete=models.CASCADE, null=True, blank=True, related_name="step"
    )

    def __str__(self) -> str:
        return f"Step number {self.amiqus_id} on record #{self.record_id}"
