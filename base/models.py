import uuid
from django.db import models
from django.utils import timezone


# Create your models here.
# models.py
class EligibleStudent(models.Model):
    ug_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=150)
    is_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.ug_number})"

    class Meta:
        ordering = ("full_name",)


class Event(models.Model):
    name = models.CharField(max_length=255)
    registration_open = models.BooleanField(default=True)
    reveal_open = models.BooleanField(default=False)

    countdown_datetime = models.DateTimeField(null=True, blank=True)
    reveal_datetime = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_countdown_active(self):
        return self.countdown_datetime and self.countdown_datetime > timezone.now()

    @property
    def is_reveal_active(self):
        return self.reveal_datetime and self.reveal_datetime > timezone.now()

    def __str__(self):
        return self.name


def _generate_token():
    return uuid.uuid4().hex[:8]


class Participant(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="participants")

    full_name = models.CharField(max_length=255)
    ug_number = models.CharField(max_length=50)

    # Secure access token for reveal
    reveal_token = models.CharField(
        default=_generate_token, editable=False, unique=True)

    assigned_to = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_from"
    )

    has_revealed = models.BooleanField(default=False)
    eligible_record = models.OneToOneField(
        EligibleStudent, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("event", "ug_number")

    @property
    def avatar_initials(self):
        parts = [part for part in self.full_name.split() if part]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0][:1].upper()
        return f"{parts[0][:1]}{parts[-1][:1]}".upper()

    def __str__(self):
        return f"{self.full_name} ({self.ug_number})"
