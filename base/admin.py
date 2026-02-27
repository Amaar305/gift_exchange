from django.contrib import admin
from .models import Event, Participant, EligibleStudent


# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_open",
                    "reveal_open", "countdown_datetime")
    list_filter = ("registration_open", "reveal_open")
    search_fields = ("name",)


@admin.register(EligibleStudent)
class EligibleStudentAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "ug_number")
    list_filter = ("is_registered", )
    search_fields = ("ug_number", "full_name")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "ug_number",
                    "has_revealed", "created_at")
    list_filter = ("has_revealed", "created_at")
    search_fields = ("ug_number", "full_name")
