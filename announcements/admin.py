from django.contrib import admin
from .models import Announcement, AnnouncementAudience

class AnnouncementAudienceInline(admin.TabularInline):
    model = AnnouncementAudience
    extra = 1
    fields = ('student', 'teacher', 'parent')
    autocomplete_fields = ['student', 'teacher', 'parent']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'start_date', 'created_at')
    search_fields = ('title', 'message')
    date_hierarchy = 'start_date'
    fieldsets = (
        (None, {
            'fields': ('title', 'message', 'is_active')
        }),
        ('Date Information', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )
    inlines = [AnnouncementAudienceInline]
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected announcements as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected announcements as inactive"

@admin.register(AnnouncementAudience)
class AnnouncementAudienceAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'get_student', 'get_teacher', 'get_parent')
    list_filter = ('announcement',)
    search_fields = ('announcement__title', 'student__user__first_name', 
                    'teacher__user__first_name', 'parent__user__first_name')

    def get_student(self, obj):
        return obj.student.user.get_full_name() if obj.student else None
    get_student.short_description = 'Student'

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else None
    get_teacher.short_description = 'Teacher'

    def get_parent(self, obj):
        return obj.parent.user.get_full_name() if obj.parent else None
    get_parent.short_description = 'Parent'