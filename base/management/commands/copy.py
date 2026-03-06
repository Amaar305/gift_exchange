from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from base.models import Event, EligibleStudent, Participant
from base.services import generate_assignments


class Command(BaseCommand):
    help = "Generate gift exchange assignments for an event"

    def handle(self, *args, **options):

        try:
            st = EligibleStudent.objects.all()
            for s in st:
                p = Participant.objects.create(
                    event=Event.objects.first(),
                    full_name=s.full_name,
                    ug_number=s.ug_number,
                    eligible_record=s
                )
                p.save()
            # generate_assignments(Event.objects.first())
        except ValidationError as e:
            raise CommandError(str(e))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated assignments for event:"
            )
        )
