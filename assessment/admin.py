from django.contrib import admin
from .models import Exam, Assignment, Grade, Result

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview')
    search_fields = ('name', 'description')
    list_per_page = 20

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade', 'teacher_name', 'exam_date', 'created_at')
    list_filter = ('subject', 'grade', 'exam_date', 'teacher')
    search_fields = ('title', 'subject__name', 'teacher__user__first_name')
    date_hierarchy = 'exam_date'
    raw_id_fields = ('teacher',)
    ordering = ('-exam_date',)

    def teacher_name(self, obj):
        return obj.teacher.user.get_full_name()
    teacher_name.short_description = 'Teacher'

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'grade', 'teacher_name', 'due_date', 'days_remaining')
    list_filter = ('subject', 'grade', 'due_date')
    search_fields = ('title', 'subject__name')
    date_hierarchy = 'due_date'
    raw_id_fields = ('teacher',)

    def teacher_name(self, obj):
        return obj.teacher.user.get_full_name()
    teacher_name.short_description = 'Teacher'

    def days_remaining(self, obj):
        from django.utils import timezone
        delta = obj.due_date - timezone.now().date()
        return f"{delta.days} days"
    days_remaining.short_description = 'Deadline'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'assessment_type', 'assessment_title', 'score', 'graded_on')
    list_filter = ('exam__subject', 'assignment__subject', 'graded_on')
    search_fields = ('student__user__first_name', 'exam__title', 'assignment__title')
    raw_id_fields = ('student', 'exam', 'assignment')
    date_hierarchy = 'graded_on'

    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'

    def assessment_type(self, obj):
        return 'Exam' if obj.exam else 'Assignment'
    assessment_type.short_description = 'Type'

    def assessment_title(self, obj):
        return obj.exam.title if obj.exam else obj.assignment.title
    assessment_title.short_description = 'Assessment'