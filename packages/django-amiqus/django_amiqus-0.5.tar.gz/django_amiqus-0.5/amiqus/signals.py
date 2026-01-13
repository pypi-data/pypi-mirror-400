"""
Amiqus signals.

Signals are fired when corresponding callbacks are received.

See https://developers.amiqus.co/guides/webhooks.html

"""

from django.dispatch import Signal

# fired after the status of a check /record is updated
# e.g. (obj, 'check.completed', 'pending', 'complete')
# providing_args=["instance", "event", "status_before", "status_after"]
on_status_change = Signal()

# 'complete' is the terminal state of both records and checks, and as
# such it gets special treatment - it's the event that most people will
# be interested, so instead of having to filter out the on_status_change
# signal that results in completion, we have a dedicated signal.
# providing_args=["instance", "completed_at"]
on_completion = Signal()

# Signal that will be sent when a record is reviewed
record_reviewed = Signal()
