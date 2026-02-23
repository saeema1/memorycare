from django.contrib import admin
from .models import CognitiveTest, TestResult, MoodEntry


@admin.register(CognitiveTest)
class CognitiveTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'max_score', 'created_at']
    list_filter = ['test']
    search_fields = ['user__username', 'test__name']


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'created_at']
    list_filter = ['mood']
    search_fields = ['user__username']


from .models import DailyActivity

@admin.register(DailyActivity)
class DailyActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'activity_type', 'scheduled_for', 'completed']
    list_filter = ['activity_type', 'completed']
    search_fields = ['user__username', 'name']


from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type', 'patient', 'caregiver', 'is_read', 'created_at']
    list_filter = ['alert_type', 'is_read']
    search_fields = ['patient__username', 'caregiver__username', 'message']