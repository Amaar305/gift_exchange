from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from .models import Event, Participant
from .services import get_event_statistics, register_participant, reveal_assignment

# Create your views here.


def landing_view(request):
    return render(request, "base/landing.html")


def splash_view(request):
    return render(request, "base/splash.html")


def eligibity_view(request):
    return render(request, "base/eligibility.html")


def register_view(request):
    event = Event.objects.first()

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        ug_number = request.POST.get("ug_number")

        try:
            participant = register_participant(event, full_name, ug_number)
            success_url = f"/partials/register_success.html?participant_id={participant.id}"
            if request.headers.get("HX-Request") == "true":
                response = HttpResponse(status=204)
                response["HX-Redirect"] = success_url
                return response
            return redirect(success_url)
        except ValidationError as e:
            return render(request, "base/partials/register_error.html", {
                "error": str(e)
            })
    return render(request, "base/register.html")


def register_success_view(request):
    event = Event.objects.first()
    participant_id = request.GET.get("participant_id")
    participant = get_object_or_404(
        Participant, id=participant_id, event=event)
    return render(request, "base/partials/register_success.html", {
        "participant": participant,
        "event": event
    })


def reveal_view(request):
    event = Event.objects.first()

    if request.method == "POST":
        ug_number = request.POST.get("ug_number")
        token = request.POST.get("token")

        try:
            assigned = reveal_assignment(event, ug_number, token)
            success_url = f"{reverse('reveal_result')}?assigned_id={assigned.id}"
            if request.headers.get("HX-Request") == "true":
                response = HttpResponse(status=204)
                response["HX-Redirect"] = success_url
                return response
            return redirect(success_url)
        except ValidationError as e:
            return render(request, "base/partials/reveal_error.html", {
                "error": str(e)
            })

    return render(request, "base/reveal.html", {
        "event": event
    })


def reveal_result_view(request):
    event = Event.objects.first()
    assigned_id = request.GET.get("assigned_id")
    assigned = get_object_or_404(Participant, id=assigned_id, event=event)
    return render(request, "base/partials/reveal_result.html", {
        "assigned": assigned,
        "event": event
    })

# @staff_member_required


def dashboard_view(request):
    event = Event.objects.first()
    if not event:
        return render(request, "base/dashboard.html", {
            "stats": {
                "participants": [],
                "total_registered": 0,
                "total_revealed": 0,
                "not_revealed": [],
            },
            "event": None,
            "dashboard": {
                "status_filter": "all",
                "participants": [],
                "shown_count": 0,
                "reveal_percent": 0,
                "pending_percent": 0,
                "countdown_iso": "",
            },
        })

    stats = get_event_statistics(event)
    if request.method == "POST":
        date = request.POST.get("countdown_datetime")
        event.countdown_datetime = date
        event.save()
        event.refresh_from_db()

    status_filter = request.GET.get("status", "all").strip().lower()
    if status_filter not in {"all", "revealed", "pending"}:
        status_filter = "all"

    participants = stats["participants"]
    if status_filter == "revealed":
        participants = participants.filter(has_revealed=True)
    elif status_filter == "pending":
        participants = participants.filter(has_revealed=False)

    total_registered = stats["total_registered"]
    total_revealed = stats["total_revealed"]
    pending_count = max(total_registered - total_revealed, 0)
    reveal_percent = round((total_revealed / total_registered) * 100) if total_registered else 0
    pending_percent = max(100 - reveal_percent, 0)
    countdown_iso = (
        timezone.localtime(event.countdown_datetime).strftime("%Y-%m-%dT%H:%M")
        if event.countdown_datetime else ""
    )

    return render(request, "base/dashboard.html", {
        "stats": stats,
        "event": event,
        "dashboard": {
            "status_filter": status_filter,
            "participants": participants,
            "shown_count": participants.count(),
            "pending_count": pending_count,
            "reveal_percent": reveal_percent,
            "pending_percent": pending_percent,
            "countdown_iso": countdown_iso,
        },
    })

# base/urls.py
