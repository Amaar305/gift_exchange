from .models import Event


def event(request):
    # Cache per request so repeated access in the same render path is cheap.
    if not hasattr(request, "_current_event"):
        request._current_event = Event.objects.first()
    return {"event": request._current_event}
