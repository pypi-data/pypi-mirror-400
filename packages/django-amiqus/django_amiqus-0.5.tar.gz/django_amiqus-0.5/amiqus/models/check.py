from __future__ import annotations

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from dateutil.parser import parse as date_parse
from ..settings import scrub_check_data
from .base import BaseQuerySet, BaseStatusModel
from .record import Record

logger = logging.getLogger(__name__)


class CheckQuerySet(BaseQuerySet):
    """Check model queryset."""

    def create_check(self, record: Record, raw: dict) -> Check:
        """Create a new Check from the raw JSON."""
        logger.debug("Creating new Amiqus check from JSON: %s", raw)
        return Check(user=record.user, amiqus_record=record).parse(raw).save()


class Check(BaseStatusModel):
    """Specific checks associated with a Record."""

    class CheckStatus(models.TextChoices):
        """Combined list of states values for record / check."""

        PENDING = ("pending", _("Pending"))
        SUBMITTED = ("submitted", _("Submitted"))
        ACCEPTED = ("accepted", _("Accepted"))
        REJECTED = ("rejected", _("Cancelled"))
        REFER = ("refer", _("Refer"))
        FAILED = ("failed", _("Failed"))
        PAUSED = ("paused", _("Paused"))

    base_href = "checks"

    class CheckType(models.TextChoices):
        """
        Represent the various types of Check that Amiqus supports.

        Note that some of these require various preferences to be set.
        See the steps array in the create record documentation:
        https://developers.amiqus.co/aqid/api-reference.html#tag/Records/operation/post-records
        """

        CREDIT_REPORT = ("check.credit", "Credit Report")
        CRIMINAL_RECORD = ("check.criminal_record", "Criminal Record")
        IDENTITY_REPORT = ("check.identity", "Identity Report")
        PHOTO_ID = ("check.photo_id", "Photo ID")
        EMPLOYMENT_REFERENCING = (
            "check.employment_referencing",
            "Employment Referencing",
        )
        EMPLOYMENT_HISTORY = ("check.reference", "Employment History")
        FACE_CAPTURE = ("check.video", "Face Capture")
        WATCHLIST = ("check.watchlist", "Watchlist")
        # For testing
        DUMMY = ("check.dummy", "Dummy")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_(
            "The Django user (denormalised from Client to make navigation easier)."
        ),  # noqa
        related_name="amiqus_checks",
    )
    amiqus_record = models.ForeignKey(
        Record,
        on_delete=models.CASCADE,
        help_text=_("Record to which this check is attached."),
        related_name="checks",
    )
    check_type = models.CharField(
        max_length=50,
        choices=CheckType.choices,
        help_text=_(
            "The name of the check - see https://developers.amiqus.co/aqid/api-reference.html#tag/Records/operation/get-checks-id"
        ),
    )

    objects = CheckQuerySet.as_manager()

    def __str__(self) -> str:
        return "{} for {}".format(self.get_check_type_display().capitalize(), self.user)

    def __repr__(self) -> str:
        return "<Check id={} type='{}' user_id={}>".format(
            self.id, self.check_type, self.user.id
        )

    def parse(self, raw_json: dict) -> Check:
        """
        Parse the raw value out into other properties.

        Before parsing the data, this method will call the
        scrub_check_data function to remove sensitive data
        so that it is not saved into the local object.

        """
        super().parse(scrub_check_data(raw_json))
        # Ensure that the check type conforms to Check.CheckType.
        # On Record/Check creation, the type will have the check.
        # prefix. But when pulling check data, there is no prefix.
        self.check_type = (
            self.raw["type"]
            if self.raw["type"].startswith("check.")
            else "check.{}".format(self.raw["type"])
        )

        # From the create_record endpoint, the ID of the Check is
        # given by the check key. But when retrieving a Check, it
        # is given by the id key. So we should use either.
        self.amiqus_id = self.raw.get("check") or self.raw["id"]
        self.updated_at = date_parse(self.raw.get("updated_at"))
        return self
