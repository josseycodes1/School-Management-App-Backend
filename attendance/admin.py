from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'class_name', 'date', 'status', 'recorded_by_name', 'created_at')
    list_filter = ('status', 'date', 'class_ref', 'recorded_by')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'class_ref__name')
    date_hierarchy = 'date'
    list_editable = ('status',)  # Allows quick editing directly from list view
    ordering = ('-date', 'class_ref')
    raw_id_fields = ('student', 'recorded_by')  # Better for large student/teacher lists

    fieldsets = (
        (None, {
            'fields': ('student', 'class_ref', 'date', 'status')
        }),
        ('Record Information', {
            'fields': ('recorded_by',),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student__user__first_name'

    def class_name(self, obj):
        return obj.class_ref.name
    class_name.short_description = 'Class'
    class_name.admin_order_field = 'class_ref__name'

    def recorded_by_name(self, obj):
        return obj.recorded_by.user.get_full_name() if obj.recorded_by else "System"
    recorded_by_name.short_description = 'Recorded By'