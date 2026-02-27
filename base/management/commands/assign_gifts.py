from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from base.models import Event
from base.services import generate_assignments


class Command(BaseCommand):
    help = "Generate gift exchange assignments for an event"

    def add_arguments(self, parser):
        parser.add_argument("--event_id", type=int, required=True)

    def handle(self, *args, **options):
        event_id = options["event_id"]

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise CommandError("Event does not exist.")

        try:
            generate_assignments(event)
        except ValidationError as e:
            raise CommandError(str(e))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated assignments for event: {event.name}"
            )
        )