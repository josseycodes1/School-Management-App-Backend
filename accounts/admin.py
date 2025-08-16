from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AdminProfile, ParentProfile, TeacherProfile, StudentProfile
from .models import Subject, Classes, Lesson

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'gender')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
admin.site.register(AdminProfile, ProfileAdmin)
admin.site.register(ParentProfile, ProfileAdmin)
admin.site.register(TeacherProfile, ProfileAdmin)
admin.site.register(StudentProfile, ProfileAdmin)

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_teacher', 'created_at')
    list_filter = ('teacher', 'created_at') 
    search_fields = ('name',)
    ordering = ('name',)

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else "Not assigned"
    get_teacher.short_description = 'Teacher'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_class', 'get_teacher', 'created_at')
    list_filter = ('assigned_class', 'teacher', 'created_at') 
    search_fields = ('name', 'assigned_class__name')
    raw_id_fields = ('teacher',)
    ordering = ('name',)

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name() if obj.teacher else "Not assigned"
    get_teacher.short_description = 'Teacher'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'date', 'created_at')
    list_filter = ('subject', 'date', 'created_at') 
    search_fields = ('title', 'subject__name')
    date_hierarchy = 'date'
    ordering = ('-date',)