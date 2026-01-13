from __future__ import annotations

from typing import TYPE_CHECKING

import simplejson as json  # simplejson supports Decimal
from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Check, Client, Event, Record, Step, Form, Review

if TYPE_CHECKING:
    from .models.base import BaseModel


class ResultMixin(object):
    """Adds custom action for overriding is_clear."""

    def mark_as_clear(self, request: HttpRequest, queryset: models.QuerySet) -> None:
        """Call mark_as_clear on all objects in the queryset."""
        for obj in queryset:
            obj.mark_as_clear(request.user)

    mark_as_clear.short_description = _("Mark selected items as clear")  # type: ignore


class EventsMixin(object):
    """Pretty print Events relating to an object."""

    def _events(self, obj: Event) -> str:
        """Pretty print object events."""
        events = obj.events()
        html = "".join(
            ["<li>{}: {}</li>".format(e.completed_at.date(), e.action) for e in events]
        )
        return mark_safe("<ul>{}</ul>".format(html))  # noqa: S703, S308

    _events.short_description = _("Related events")  # type: ignore


class RawMixin(object):
    """Admin mixin used to pprint raw JSON fields."""

    def _raw(self, obj: BaseModel) -> str:
        """
        Return an indented HTML pretty-print version of JSON.

        Take the event_payload JSON, indent it, order the keys and then
        present it as a <code> block. That's about as good as we can get
        until someone builds a custom syntax function.

        """
        pretty = json.dumps(obj.raw, sort_keys=True, indent=4, separators=(",", ": "))
        html = pretty.replace(" ", "&nbsp;").replace("\n", "<br>")
        return mark_safe("<code>{}</code>".format(html))  # noqa: S703, S308

    _raw.short_description = _("Raw (from API)")  # type: ignore


class UserMixin(object):
    """Admin mixin used to add _user function."""

    def _user(self, obj: Client | Record | Check) -> str:
        """
        Return user's real name.

        It's impossible to create an Client in the Amiqus API
        with a blank first/last name, so assuming that get_full_name
        will not be blank.

        """
        return obj.user.get_full_name().title()

    _user.short_description = "User"  # type: ignore


class ClientAdmin(RawMixin, UserMixin, admin.ModelAdmin):
    """Admin model for Client objects."""

    list_display = ("amiqus_id", "_user", "created_at")
    list_filter = ("created_at",)
    ordering = ("user__first_name", "user__last_name", "user__username")
    readonly_fields = ("amiqus_id", "user", "created_at", "_raw")
    search_fields = ("amiqus_id", "user__first_name", "user__last_name")
    raw_id_fields = ("user",)
    exclude = ("raw",)


admin.site.register(Client, ClientAdmin)


class RecordAdmin(ResultMixin, EventsMixin, RawMixin, UserMixin, admin.ModelAdmin):
    """Admin model for Record objects."""

    list_display = (
        "amiqus_id",
        "_user",
        "status",
        "created_at",
        "updated_at",
        "is_clear",
    )
    readonly_fields = (
        "amiqus_id",
        "user",
        "created_at",
        "client",
        "status",
        "updated_at",
        "_raw",
        "_events",
    )
    search_fields = ("amiqus_id", "user__first_name", "user__last_name")
    list_filter = ("created_at", "updated_at", "status")
    ordering = ("user__first_name", "user__last_name")
    raw_id_fields = ("client", "user")
    exclude = ("raw",)
    actions = ("mark_as_clear",)


admin.site.register(Record, RecordAdmin)


class CheckAdmin(ResultMixin, EventsMixin, RawMixin, UserMixin, admin.ModelAdmin):
    """Admin model for Check objects."""

    list_display = (
        "amiqus_id",
        "_user",
        "check_type",
        "status",
        "created_at",
        "updated_at",
        "is_clear",
    )
    ordering = ("user__first_name", "user__last_name")
    readonly_fields = (
        "amiqus_id",
        "user",
        "amiqus_record",
        "check_type",
        "status",
        "created_at",
        "updated_at",
        "_raw",
    )
    search_fields = (
        "amiqus_id",
        "amiqus_record__amiqus_id",
        "user__first_name",
        "user__last_name",
    )
    list_filter = ("created_at", "updated_at", "check_type", "status")
    raw_id_fields = ("amiqus_record", "user")
    exclude = ("raw",)
    actions = ("mark_as_clear",)


admin.site.register(Check, CheckAdmin)


class EventAdmin(RawMixin, UserMixin, admin.ModelAdmin):
    """Admin model for Event objects."""

    list_display = (
        "amiqus_id",
        "resource_type",
        "_user",
        "action",
        "status",
        "completed_at",
    )
    list_filter = ("action", "resource_type", "status", "completed_at")
    readonly_fields = (
        "amiqus_id",
        "resource_type",
        "action",
        "status",
        "completed_at",
        "received_at",
        "_raw",
    )
    search_fields = ("amiqus_id",)
    exclude = ("raw",)


admin.site.register(Event, EventAdmin)


class StepAdmin(RawMixin, admin.ModelAdmin):
    """Admin model for Step objects."""

    def reviews(self, obj: Step) -> str:
        """Return a list of reviews for the step."""
        reviews = obj.reviews.all()
        if reviews.count() == 0:
            return "No reviews"
        html = "".join(
            [
                "<li>{}: {}</li>".format(review.created_at.date(), review.status)
                for review in reviews
            ]
        )
        return mark_safe("<ul>{}</ul>".format(html))  # noqa: S703, S308

    list_display = (
        "id",
        "record",
        "amiqus_check",
        "form",
    )
    readonly_fields = (
        "id",
        "record",
        "amiqus_id",
        "amiqus_check",
        "form",
        "reviews",
    )
    search_fields = ("id",)
    raw_id_fields = ("record", "amiqus_check", "form")


class FormAdmin(RawMixin, admin.ModelAdmin):
    """Admin model for Form objects."""

    list_display = (
        "amiqus_id",
        "created_at",
    )
    list_filter = ("created_at",)
    readonly_fields = (
        "amiqus_id",
        "created_at",
        "_raw",
    )
    search_fields = ("amiqus_id",)
    exclude = ("raw",)


class ReviewAdmin(RawMixin, admin.ModelAdmin):
    """Admin model for Review objects."""

    list_display = (
        "amiqus_id",
        "created_at",
        "status",
    )
    list_filter = ("created_at", "status")
    readonly_fields = ("status", "step", "amiqus_id", "created_at", "_raw")
    search_fields = ("amiqus_id",)
    exclude = ("raw",)


admin.site.register(Step, StepAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Review, ReviewAdmin)
