"""
Amiqus webhook handler.

The Amiqus API will send a webhook to the configured URL when an event
occurs, which we then use to update the relevant object.

"""

from __future__ import annotations

import json
import logging

from django.http import HttpRequest, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from .decorators import verify_signature
from .models import Client, Event, Record
from .settings import LOG_EVENTS
from .signals import record_reviewed
from .helpers import create_or_update_reviews

logger = logging.getLogger(__name__)


@csrf_exempt
@verify_signature()
def status_update(request: HttpRequest) -> HttpResponse:  # noqa: C901
    """
    Handle event callbacks from the API.

    This is the request handler which does little other than log the
    request and call the _webhook function which does the processing.
    Done like this to make it easier to test without having to set up
    request objects.

    NB This view function will always return a 200 status - in order to
    prevent Amiqus from endlessly retrying. The only exceptions to this
    are caused by the verify_signature decorator - if it cannot verify
    the callback, then it will return a 403 - which should be ok, as if
    Amiqus sends the request it should never fail...

    """
    received_at = now()
    logger.debug("Received Amiqus callback: %s", request.body)
    if not (data := json.loads(request.body)):
        logger.exception("Received empty Amiqus webhook body.")
        return HttpResponse("Empty webhook.")
    try:
        trigger = data["trigger"]
        alias = trigger["alias"]
    except KeyError:
        logger.exception("Invalid Amiqus webhook body.")
        return HttpResponse("Invalid webhook body.")

    entity_type = alias.split(".")[0]
    if entity_type not in ("client", "record"):
        logger.error("Invalid entity_type: %s", entity_type)
        return HttpResponse("Invalid event trigger.")
    event = Event(received_at=received_at)

    try:
        resource = event.parse(data, entity_type=entity_type).resource
        resource.update_status(event)

        # Send signal for record.reviewed events
        if alias == "record.reviewed":
            logger.debug("Sending record_reviewed signal for record %s", resource.id)
            create_or_update_reviews(event)
            record_reviewed.send(
                sender=resource.__class__, record=resource, event=event, data=data
            )

        if LOG_EVENTS:
            event.save()
        return HttpResponse("Update processed.")
    except KeyError as ex:
        logger.exception("Missing Amiqus event content.", exc_info=ex)
        return HttpResponse("Unexpected event content.")
    except ValueError:
        logger.exception("Unknown Amiqus resource type: %s", event.resource_type)
        return HttpResponse("Unknown resource type.")
    except Record.DoesNotExist:
        # TODO(source-of-truth) Create Record when *new* request is spawned from Amiqus
        # Missing Records can be synchronised as we utilise a reference shared
        # between the user, and Amiqus itself.
        logger.exception("Amiqus record does not exist: %s", event.amiqus_id)
        # 1. Get Record from API.
        # 2. Get Client attached to Record
        # 3. Use their reference to match with a user on system
        # 4. Create record as normal
        return HttpResponse("Record not found.")
    except Client.DoesNotExist:
        logger.warning("Amiqus client does not exist: %s", event.amiqus_id)
        return HttpResponse("Client not found.")
    except Exception:  # noqa: B902
        logger.exception("Amiqus update could not be processed.")
        return HttpResponse("Unknown error.")
