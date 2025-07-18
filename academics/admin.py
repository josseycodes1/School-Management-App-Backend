from django.contrib import admin
from .models import Subject, Classes, Lesson

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_teacher', 'created_at')
    list_filter = ('teacher', 'created_at')  # Added filter for teacher and creation date
    search_fields = ('name',)
    ordering = ('name',)

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else "Not assigned"
    get_teacher.short_description = 'Teacher'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_class', 'get_teacher', 'created_at')
    list_filter = ('assigned_class', 'teacher', 'created_at')  # Added multiple filters
    search_fields = ('name', 'assigned_class__name')
    raw_id_fields = ('teacher',)
    ordering = ('name',)

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else "Not assigned"
    get_teacher.short_description = 'Teacher'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'date', 'created_at')
    list_filter = ('subject', 'date', 'created_at')  # Enhanced filters
    search_fields = ('title', 'subject__name')
    date_hierarchy = 'date'
    ordering = ('-date',)