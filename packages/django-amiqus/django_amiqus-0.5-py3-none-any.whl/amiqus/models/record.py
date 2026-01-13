from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dateutil.parser import parse as date_parse
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseQuerySet, BaseStatusModel

if TYPE_CHECKING:
    from .client import Client

logger = logging.getLogger(__name__)


class RecordQuerySet(BaseQuerySet):
    """Record model manager."""

    def create_record(self, client: Client, raw: dict) -> Record:
        """Create a new Record object and its related objects from the API response."""
        logger.debug("Creating new Amiqus record from JSON: %s", raw)

        # Create the base record
        perform_url = raw.get("perform_url") or ""
        record = Record.objects.create(
            user=client.user,
            client=client,
            amiqus_id=raw["id"],
            status=raw["status"],
            created_at=date_parse(raw["created_at"]),
            perform_url=perform_url,
            raw=raw,
        )

        # Create all related objects
        self._create_steps_from_response(record, raw)

        return record

    def _create_steps_from_response(self, record: Record, raw: dict) -> None:
        """Create Steps and their related Check/Form objects from API response."""
        from .check import Check
        from .form import Form
        from .step import Step

        for step_data in raw.get("steps", []):
            if "check" in step_data.get("type"):
                check = Check.objects.create(
                    amiqus_id=step_data["check"],
                    amiqus_record=record,
                    check_type=step_data["type"],
                    user=record.user,
                )
                Step.objects.create(
                    amiqus_id=step_data["id"],
                    amiqus_check=check,
                    record=record,
                )
            elif "form" in step_data.get("type"):
                form = Form.objects.create(
                    amiqus_id=step_data["form"],
                    record=record,
                    user=record.user,
                )
                Step.objects.create(
                    amiqus_id=step_data["id"],
                    form=form,
                    record=record,
                )


class Record(BaseStatusModel):
    """The state of an individual record made against an Client."""

    base_href = "records"

    class RecordStatus(models.TextChoices):
        PENDING = ("pending", _("Pending"))
        STARTED = ("started", _("Started"))
        COMPLETE = ("complete", _("Complete"))
        INCOMPLETE = ("incomplete", _("Incomplete"))
        WAITING = ("waiting", _("Waiting"))
        FAILED = ("failed", _("Failed"))
        EMPTY = ("empty", _("Empty"))
        AMENDMENTS = ("amendments", _("Amendments"))
        PAUSED = ("paused", _("Paused"))
        REVIEWED = ("reviewed", _("Reviewed"))
        UNKNOWN = ("unknown", _("Unknown"))

    class RecordType(models.TextChoices):
        CREDIT = "credit"
        CRIMINAL_RECORD = "criminal_record"
        DOCUMENT = "document"
        DUMMY = "dummy"
        IDENTITY = "identity"
        THORNTONS_ONBOARDING = "thorntons_onboarding"
        WATCHLIST = "watchlist"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "The Django user (denormalised from Client to make navigation easier)."
        ),  # noqa
        related_name="amiqus_records",
    )

    perform_url = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        help_text=_("The current status of the record / check (from API)."),
        choices=RecordStatus.choices,
        db_index=True,
        blank=True,
        null=True,
    )

    client = models.ForeignKey(
        "amiqus.Client",
        on_delete=models.CASCADE,
        help_text=_("The client for whom the record is being made."),
        related_name="records",
    )

    objects = RecordQuerySet.as_manager()

    def __str__(self) -> str:
        return f"Amiqus record for {self.user}"

    def __repr__(self) -> str:
        return (
            f"<Record amiqus_id={self.amiqus_id} id={self.id} user_id={self.user_id}>"
        )
