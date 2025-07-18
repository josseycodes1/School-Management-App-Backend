from django.contrib import admin
from .models import Event, EventParticipant

class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1
    fields = ('get_participant', 'registered_at')
    readonly_fields = ('get_participant', 'registered_at')
    max_num = 0  # Makes it read-only for display purposes

    def get_participant(self, obj):
        participant = obj.student or obj.teacher or obj.parent
        return f"{participant.user.get_full_name()} ({participant.user.role})"
    get_participant.short_description = 'Participant'

    def has_add_permission(self, request, obj=None):
        return False  # Disable adding through inline

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'participant_count', 'days_until')
    list_filter = ('date', 'location')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'
    ordering = ('-date',)
    inlines = [EventParticipantInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Event Details', {
            'fields': ('date', 'location'),
            'classes': ('collapse',)
        }),
    )
    actions = ['send_reminders']

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Attendees'

    def days_until(self, obj):
        from django.utils import timezone
        delta = obj.date - timezone.now()
        return f"In {delta.days} days" if delta.days > 0 else f"{-delta.days} days ago"
    days_until.short_description = 'Timing'

    def send_reminders(self, request, queryset):
        from django.contrib import messages
        messages.success(request, f"Reminders sent for {queryset.count()} events")
    send_reminders.short_description = "Send reminders to participants"

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'participant_type', 'participant_name', 'registered_at')
    list_filter = ('event', 'registered_at')
    search_fields = (
        'event__title',
        'student__user__first_name',
        'teacher__user__first_name',
        'parent__user__first_name'
    )
    raw_id_fields = ('student', 'teacher', 'parent')

    def participant_name(self, obj):
        participant = obj.student or obj.teacher or obj.parent
        return participant.user.get_full_name()
    participant_name.short_description = 'Name'

    def participant_type(self, obj):
        if obj.student: return 'Student'
        if obj.teacher: return 'Teacher'
        if obj.parent: return 'Parent'
        return 'Unknown'
    participant_type.short_description = 'Type'