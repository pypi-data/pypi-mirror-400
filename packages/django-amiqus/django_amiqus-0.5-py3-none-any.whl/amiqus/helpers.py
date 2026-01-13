from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Union

from django.conf import settings

from .api import get, patch, post
from .models import Client, Event, Record, Review


def create_client(user: settings.AUTH_USER_MODEL, **kwargs: Any) -> Client:
    """
    Create an client in the Amiqus system.

    Args:
        user: a Django User instance to register as a Client.
    Kwargs:
       any kwargs passed in are merged into the data dict sent to the
       API. This enables support for additional client properties - e.g
       dob, gender, country, and any others that may change over time.

    """
    data = {
        "name": {
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "email": user.email,
    }
    data.update(kwargs)
    response = post("clients", data=data)
    return Client.objects.create_client(user, response)


def create_record(
    client: Client,
    steps: list[dict[str, Any]],
    notification: Union[Literal["email"], Literal[False]] = "email",
    reminder: bool = True,
) -> Record:
    """
    Create a new Record (and child Steps).

    Args:
        client: Client for whom the records are being made.
        steps: list of dicts, each of which is a step in the record. These
        should be structured according to the documentation linked below. Example:
        [
            {
                "type": "check.dummy",
                "preferences": {"report_type": "standard"}
            }
        ]
        notification: Either "email" or False to control notification behavior.
        reminder: Whether to send a reminder email to the client.

    Returns a new Record object, and creates the child Steps.

    https://developers.amiqus.co/aqid/api-reference.html#tag/Records/operation/post-records

    """
    # We can add a custom message to the link here if we like, with a "message"
    # key in the data dict.
    data = {
        "client": client.amiqus_id,
        "notification": notification,
        "reminder": reminder,
        "steps": steps,
    }

    response = post("records", data=data)
    return Record.objects.create_record(client=client, raw=response)


def create_or_update_reviews(
    event: Event,
) -> None:
    """Create or update reviews for each step in a record."""
    record_id = event.raw["data"]["record"]["id"]
    record = Record.objects.get(amiqus_id=record_id)
    steps = record.steps.all()

    for step in steps:
        response = get(f"records/{record_id}/steps/{step.amiqus_id}/reviews")
        review_list = response["data"]

        for review_data in review_list:
            try:
                review = Review.objects.get(amiqus_id=review_data["id"])
                if review.status != review_data["status"]:
                    review.parse(review_data).save()
            except Review.DoesNotExist:
                Review(step=step).parse(review_data).save()


def update_client_status(client: Client, client_status: Client.ClientStatus) -> None:
    """Update the status of a client."""
    response = patch(
        f"clients/{client.amiqus_id}", data={"status": client_status.value}
    )
    client.parse(response).save()


def update_record_expired_at_date(record: Record, expired_at: datetime) -> None:
    """
    Update the expired_at date of a record.

    The expired_at date determines the date by which the client needs to complete
    the required checks. Updating it with a future date will extend this deadline.
    Value for expiry date must be within 10 days from now.
    """
    response = patch(
        f"records/{record.amiqus_id}",
        data={"expired_at": expired_at.strftime("%Y-%m-%dT%H:%M:%SZ")},
    )
    record.parse(response).save()
