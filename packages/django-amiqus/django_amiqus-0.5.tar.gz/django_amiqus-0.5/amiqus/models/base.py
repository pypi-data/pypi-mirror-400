from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING, Any

from dateutil.parser import parse as date_parse
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..api import get
from ..signals import on_completion, on_status_change

if TYPE_CHECKING:
    from .event import Event

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    """Base model used to set timestamps."""

    # used to format the href - override in subclasses
    base_href = ""

    # Should this be an integer field?
    amiqus_id = models.CharField(
        "Amiqus ID",
        unique=True,
        max_length=40,
        help_text=_("The id returned from the Amiqus API."),
    )
    created_at = models.DateTimeField(
        help_text=_("The timestamp returned from the Amiqus API."),
        blank=True,
        null=True,
    )
    raw = models.JSONField(
        help_text=_("The raw JSON returned from the API."), blank=True, null=True
    )

    class Meta:
        abstract = True

    @property
    def href(self) -> str:
        """Return the href from base_href."""
        return f"{self.base_href}/{self.amiqus_id}"

    def save(self, *args: Any, **kwargs: Any) -> BaseModel:
        """Save object and return self (for chaining methods)."""
        self.full_clean()
        super().save(*args, **kwargs)
        return self

    def parse(self, raw_json: dict) -> BaseModel:
        """Parse the raw value out into other properties."""
        self.raw = raw_json
        self.amiqus_id = self.raw["id"]
        self.status = self.raw.get("status")

        created_at = self.raw.get("created_at")
        if created_at is not None:
            self.created_at = date_parse(created_at)
        else:
            self.created_at = None

        return self

    def fetch(self) -> BaseModel:
        """
        Fetch the object JSON from the remote API.

        Named after the git operation - this will call the API for the
        latest JSON representation, and update the local fields, but will
        not save the updates. This is useful for inspecting the API response
        without making permanent changes to the object. It can also be used
        to interact with the API without saving an objects:

        >>> obj = Record(amiqus_id='123').fetch()

        Returns the updated object (unsaved).

        """
        return self.parse(get(self.href))

    def pull(self) -> BaseModel:
        """
        Update the object from the remote API.

        Named after the git operation - this will call fetch(), and
        then save the object.

        Returns the updated object (saved).

        """
        return self.fetch().save()


class BaseQuerySet(models.QuerySet):
    """Custom queryset for models subclassing BaseModel."""

    def fetch(self) -> None:
        """Call fetch method on all objects in the queryset."""
        for obj in self:
            try:
                obj.fetch()
            except Exception:  # noqa: B902
                logger.exception("Failed to fetch Amiqus object: %r", obj)

    def pull(self) -> None:
        """Call pull method on all objects in the queryset."""
        for obj in self:
            try:
                obj.pull()
            except Exception:  # noqa: B902
                logger.exception("Failed to pull Amiqus object: %r", obj)


class BaseStatusModel(BaseModel):
    """Base class for models with a status field."""

    class Status(models.TextChoices):
        """Combined list of states values for record / check."""

        PENDING = ("pending", _("Pending"))
        SUBMITTED = ("submitted", _("Submitted"))
        ACCEPTED = ("accepted", _("Accepted"))
        REJECTED = ("rejected", _("Cancelled"))
        REFER = ("refer", _("Refer"))
        PAUSED = ("paused", _("Paused"))

    status = models.CharField(
        max_length=20,
        help_text=_("The current status of the record / check (from API)."),
        choices=Status.choices,
        db_index=True,
        blank=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("The timestamp of the most recent status change (from API)."),
    )

    class Meta:
        abstract = True

    def events(self) -> BaseQuerySet:
        """Return queryset of Events related to this object."""
        # prevents circ. import
        from .event import Event

        return Event.objects.filter(
            amiqus_id=self.amiqus_id, resource_type=self._meta.model_name
        )

    def update_status(self, event: Event) -> BaseStatusModel:
        """
        Update the status field of the object and fire signal(s).

        When the app receives an event callback from Amiqus, we update
        the status of the relevant Record/Check, and then fire the
        signals that allow external apps to hook in to this event.

        If the update is a change to 'complete', then we fire a second
        signal - 'complete' is the terminal state change, and therefore
        of most interest to clients - typically the on_status_update
        signal would be registered for logging a complete history of
        changes, whereas the on_completion signal would be used to do
        something more useful - updating the status of the user, sending
        them an email etc.

        Args:
            event: Event object containing the update information

        Returns the updated object.

        """
        # we're doing a lot of marshalling from JSON to python, so this assert
        # just ensures we do actually have a datetime at this point
        if not isinstance(event.completed_at, datetime.datetime):
            raise ValueError("event.completed_at is not a datetime object")
        # swap statuses around so we record old / new
        self.status, old_status = event.status, self.status
        self.updated_at = event.completed_at
        try:
            self.pull()
        except Exception:  # noqa: B902
            # even if we can't get latest, we should save the changes we
            # have already made to the object
            logger.warning("Unable to pull latest from Amiqus: '%r'", self)
            self.save()
        on_status_change.send(
            self.__class__,
            instance=self,
            event=event.action,
            status_before=old_status,
            status_after=event.status,
        )
        if event.status == self.Status.ACCEPTED.value:  # type: ignore[attr-defined]
            on_completion.send(self.__class__, instance=self)
        return self

    def parse(self, raw_json: dict) -> BaseStatusModel:
        """Parse the raw value out into other properties.

        Status models should eventually get a status, but default to None as sometimes,
        such as when they are initially returned from the API, they don't have a status.
        """
        super().parse(raw_json)
        self.status = self.raw.get("status", None)
        return self

    @property
    def is_clear(self) -> bool:
        """Return True/False to whether a record is successful and clear."""
        return self.status == self.Status.ACCEPTED.value  # type: ignore[attr-defined]
