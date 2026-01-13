from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..settings import scrub_client_data
from ..signals import on_completion, on_status_change
from .base import BaseModel, BaseQuerySet

if TYPE_CHECKING:
    from .event import Event

logger = logging.getLogger(__name__)


class ClientManager(models.Manager):
    def create_client(self, user: settings.AUTH_USER_MODEL, raw: dict) -> Client:
        """Create a new client in Amiqus from a user."""
        logger.debug("Creating new Amiqus client from JSON: %s", raw)
        client = Client(user=user)
        client.parse(raw)
        client.save()
        return client


class Client(BaseModel):
    """An Amiqus client record."""

    base_href = "clients"

    class ClientStatus(models.TextChoices):
        UNKNOWN = ("", _("Unknown"))
        APPROVED = ("approved", _("Approved"))
        REJECTED = ("rejected", _("Rejected"))
        FOR_REVIEW = ("pending", _("Needs review"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text=_("Django user that maps to this client."),
        related_name="amiqus_clients",
    )

    status = models.CharField(
        max_length=20,
        help_text=_("The current status of the Client (from API)."),
        choices=ClientStatus.choices,
        db_index=True,
        blank=True,
        null=True,
    )

    objects = ClientManager.from_queryset(BaseQuerySet)()

    def __str__(self) -> str:
        return str(self.user)

    def __repr__(self) -> str:
        return "<Client id={} user_id={}>".format(self.id, self.user.id)

    def parse(self, raw_json: dict) -> Client:
        """
        Parse the raw value out into other properties.

        Before parsing the data, this method will call the
        scrub_check_data function to remove sensitive data
        so that it is not saved into the local object.

        """
        super().parse(scrub_client_data(raw_json))
        self.status = self.raw["status"]
        return self

    def update_status(self, event: Event) -> Client:
        """
        Update the status field of a Client and fire signal(s).

        When the app receives an event callback from Amiqus, we update
        the status of the Client, and then fire the signals that allow
        external apps to hook in to this event.

        If the update is a change to 'approve', then we fire a second
        signal - 'approved' is the terminal state change, and therefore
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
        except Exception as e:  # noqa: B902
            # even if we can't get latest, we should save the changes we
            # have already made to the object
            logger.warning("Unable to pull latest from Amiqus: '%r'", self)
            self.save()
            raise e
        on_status_change.send(
            self.__class__,
            instance=self,
            event=event.action,
            status_before=old_status,
            status_after=event.status,
        )
        if event.status == self.ClientStatus.APPROVED.value:  # type: ignore[attr-defined]
            on_completion.send(self.__class__, instance=self)
        return self
