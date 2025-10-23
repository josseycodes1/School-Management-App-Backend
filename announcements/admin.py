from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'get_target_roles', 'created_at')
    list_filter = ('is_active', 'start_date', 'created_at', 'target_students', 'target_teachers', 'target_parents')
    search_fields = ('title', 'message')
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'is_active')
        }),
        ('Target Audience', {
            'fields': ('target_students', 'target_teachers', 'target_parents'),
            'classes': ('wide',)
        }),
        ('Date Information', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )
    actions = ['make_active', 'make_inactive']

    def get_target_roles(self, obj):
        return ", ".join(obj.target_roles) if obj.target_roles else "No audience"
    get_target_roles.short_description = "Target Roles"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected announcements as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected announcements as inactive"