import random
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Participant, Event, EligibleStudent
from django.utils import timezone


def validate_event_for_assignment(event: Event):
    if event.registration_open:
        raise ValidationError(
            "Registration must be closed before generating assignments.")

    if event.participants.count() < 2:
        raise ValidationError("Not enough participants.")

    already_assigned = event.participants.filter(
        assigned_to__isnull=False
    ).exists()

    if already_assigned:
        raise ValidationError(
            "Assignments already exist. Use reset before regenerating."
        )


def _generate_derangement(participants):
    shuffled = participants.copy()

    while True:
        random.shuffle(shuffled)
        if all(p != s for p, s in zip(participants, shuffled)):
            return shuffled


@transaction.atomic
def generate_assignments(event: Event):
    validate_event_for_assignment(event)

    participants = list(event.participants.select_for_update())

    shuffled = _generate_derangement(participants)

    for giver, receiver in zip(participants, shuffled):
        giver.assigned_to = receiver
        giver.save(update_fields=["assigned_to"])

    return True


def reveal_assignment(event: Event, ug_number: str, token: str):
    if event.reveal_datetime and timezone.now() < event.reveal_datetime:
        date_format = "%Y-%m-%d %H:%M:%S"
        date_str = event.reveal_datetime.strftime(date_format)
        raise ValidationError(f"Reveal is locked until {date_str}.")
    try:
        participant = event.participants.get(
            ug_number=ug_number,
            reveal_token=token
        )
    except Participant.DoesNotExist:
        raise ValidationError("Invalid UG number or token.")

    if not event.reveal_open:
        raise ValidationError("Reveal phase is not open yet.")

    if participant.has_revealed:
        raise ValidationError("You have already revealed your assignment.")

    if not participant.assigned_to:
        raise ValidationError("Assignments have not been generated yet.")

    participant.has_revealed = True
    participant.save(update_fields=["has_revealed"])

    return participant.assigned_to


def get_event_statistics(event: Event):
    participants = event.participants.select_related("assigned_to")
    total = event.participants.count()
    revealed = event.participants.filter(has_revealed=True).count()
    not_revealed = participants.filter(has_revealed=False)

    return {
        "participants": participants,
        "total_registered": total,
        "total_revealed": revealed,
        "not_revealed": not_revealed,
    }


# Registration flows
def register_participant(event: Event, full_name: str, ug_number: str):
    if not event.registration_open:
        raise ValidationError("Registration is closed.")

    try:
        eligible = EligibleStudent.objects.get(ug_number=ug_number)
    except EligibleStudent.DoesNotExist:
        raise ValidationError("You are not eligible for this gift exchange")

    if eligible.is_registered:
        raise ValidationError("You have already registered.")

    if event.participants.filter(ug_number=ug_number).exists():
        raise ValidationError("This UG number is already registered.")

    participant = Participant.objects.create(
        event=event,
        full_name=eligible.full_name,
        ug_number=ug_number.strip().upper(),
    )

    eligible.is_registered = True
    eligible.save(update_fields=["is_registered"])

    return participant


def open_reveal_phase(event: Event):
    if event.registration_open:
        raise ValidationError("Close registration before opening reveal.")

    if not event.participants.filter(assigned_to__isnull=False).exists():
        raise ValidationError("Assignments have not been generated.")

    event.reveal_open = True
    event.save(update_fields=["reveal_open"])


def close_registration(event: Event):
    if not event.registration_open:
        raise ValidationError("Registration already closed.")

    event.registration_open = False
    event.save(update_fields=["registration_open"])


@transaction.atomic
def reset_assignments(event: Event):
    participants = event.participants.select_for_update()

    if not participants.exists():
        raise ValidationError("No participants to reset.")

    participants.update(
        assigned_to=None,
        has_revealed=False
    )

    event.reveal_open = False
    event.save(update_fields=["reveal_open"])

    return True
