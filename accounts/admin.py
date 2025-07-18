from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AdminProfile, ParentProfile, TeacherProfile, StudentProfile

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