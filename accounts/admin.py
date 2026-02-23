"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Reminder


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin interface for User model"""
    
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {
            'fields': ('role',)
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'address')
        }),
        ('Assignments', {
            'fields': ('assigned_doctor', 'assigned_caregiver'),
            'classes': ('collapse',)
        }),
        ('Patient Information', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'alzheimers_duration_years'),
            'classes': ('collapse',)
        }),
        ('Caregiver Information', {
            'fields': ('specialization', 'license_number'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {
            'fields': ('role',)
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'address')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for non-superusers"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly_fields.extend(['role', 'is_superuser', 'is_staff'])
        return readonly_fields


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'scheduled_for', 'read', 'created_at']
    list_filter = ['read', 'scheduled_for']
    search_fields = ['title', 'message', 'patient__username']
