from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('DOCTOR', 'Doctor (Admin)'),
        ('CAREGIVER', 'Caregiver'),
        ('PATIENT', 'Patient'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT', help_text='User role in the system')

    # Personal fields
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    # Patient-specific
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)

    # Alzheimer's-specific: duration in years
    alzheimers_duration_years = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Duration of Alzheimer\'s in years')

    # Caregiver/Doctor-specific
    specialization = models.CharField(max_length=100, null=True, blank=True)
    license_number = models.CharField(max_length=50, null=True, blank=True)
    caregiving_experience_years = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Years of caregiving experience')
    relationship_to_patient = models.CharField(max_length=100, null=True, blank=True, help_text='Relationship to patient (e.g. Spouse)')

    # Assignments: a patient can have an assigned doctor and caregiver
    assigned_doctor = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='patients_under_doctor',
        limit_choices_to={'role': 'DOCTOR'}
    )

    assigned_caregiver = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='patients_under_caregiver',
        limit_choices_to={'role': 'CAREGIVER'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'

    @property
    def is_caregiver(self):
        return self.role == 'CAREGIVER'

    @property
    def is_patient(self):
        return self.role == 'PATIENT'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_age(self):
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Reminder(models.Model):
    """Simple reminder/notification for a patient"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    message = models.TextField()
    scheduled_for = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.patient.username}: {self.title}"
