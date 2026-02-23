from django.db import models
from django.conf import settings
from django.utils import timezone


class Alert(models.Model):
    ALERT_TYPES = [
        ('fall', 'Fall Detected'),
        ('medication', 'Missed Medication'),
        ('health', 'Health Deterioration'),
        ('other', 'Other'),
    ]

    caregiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='alerts')
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='triggered_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='other')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.patient.username}"


class CognitiveTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Questions should be a list of objects: {"text": "Q?", "choices": ["A","B"], "answer": "A"}
    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TestResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(CognitiveTest, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    max_score = models.IntegerField()
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.score}/{self.max_score})"


class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('very_happy', 'Very Happy'),
        ('happy', 'Happy'),
        ('neutral', 'Neutral'),
        ('sad', 'Sad'),
        ('very_sad', 'Very Sad'),
        ('anxious', 'Anxious'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_entries')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.get_mood_display()} @ {self.created_at.date()}"


class DailyActivity(models.Model):
    """A scheduled activity for a patient (medicine, exercise, meal, rest)."""
    ACTIVITY_TYPES = [
        ('medication', 'Medication'),
        ('exercise', 'Exercise'),
        ('meal', 'Meal'),
        ('rest', 'Rest'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_activities')
    name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='other')
    scheduled_for = models.DateTimeField()
    completed = models.BooleanField(default=False)
    last_completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    RECURRENCE_CHOICES = [
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='none')
    recurrence_interval = models.PositiveIntegerField(default=1, help_text='Interval for recurrence (e.g., every N days/weeks/months)')
    recurrence_end = models.DateField(null=True, blank=True, help_text='Optional end date for recurrence')

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return f"{self.user.username} - {self.name} @ {self.scheduled_for}" 

    def occurs_on(self, date):
        """Determine whether this activity occurs on the given date (date is a datetime.date).
        Supports simple recurrence rules: daily, weekly, monthly."""
        start_date = self.scheduled_for.date()
        if self.recurrence == 'none':
            return start_date == date

        if start_date > date:
            return False
        if self.recurrence_end and date > self.recurrence_end:
            return False

        days_diff = (date - start_date).days
        if self.recurrence == 'daily':
            return (days_diff % self.recurrence_interval) == 0
        elif self.recurrence == 'weekly':
            # match weekday and interval in weeks
            if date.weekday() != start_date.weekday():
                return False
            weeks = days_diff // 7
            return (weeks % self.recurrence_interval) == 0
        elif self.recurrence == 'monthly':
            # match day of month and interval in months
            if start_date.day != date.day:
                return False
            months = (date.year - start_date.year) * 12 + (date.month - start_date.month)
            return (months % self.recurrence_interval) == 0
        return False