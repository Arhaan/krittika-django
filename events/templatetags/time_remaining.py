from django import template
from django.utils import timezone

import math

register = template.Library()


# Custom Filter to calculate time remaining
@register.filter
def time_remaining(event):
    now = timezone.now()
    start = event.startTime
    end = event.endTime
    start_diff = (start - now).total_seconds()
    hours = math.floor(start_diff / 3600)
    if hours >= 48:
        return "(Starts in {} days)".format(math.floor(hours / 24))
    elif hours >= 24:
        return "(Starts in 1 day)"
    elif hours > 1:
        return "(Starts in {} hours)".format(hours)
    elif hours == 1:
        return "(Starts in an hour)"
    elif hours == 0:
        return "(Starts soon)"
    else:  # hours < 0
        if end:
            end_diff = (end - now).total_seconds()
            if end_diff >= 0:
                return "(Ongoing)"
            else:  # Event ended
                return ""
        else:  # end == None
            return ""
