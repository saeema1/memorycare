from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import User, Reminder


class PatientProfileTests(TestCase):
    def setUp(self):
        # Create doctor and caregiver
        self.doctor = User.objects.create_user(username='doc', password='pass', role='DOCTOR')
        self.caregiver = User.objects.create_user(username='care', password='pass', role='CAREGIVER')

        # Create patient and assign
        self.patient = User.objects.create_user(username='patient1', password='pass', role='PATIENT', email='p@example.com')
        self.patient.assigned_doctor = self.doctor
        self.patient.assigned_caregiver = self.caregiver
        self.patient.save()

        # Add a reminder
        self.reminder = Reminder.objects.create(patient=self.patient, title='Take meds', message='Take medication at 9AM', scheduled_for=timezone.now())
        # Alzheimer's duration
        self.patient.alzheimers_duration_years = 3
        self.patient.save()

    def test_profile_requires_login(self):
        url = reverse('accounts:profile')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_profile_shows_assignments(self):
        self.client.login(username='patient1', password='pass')
        resp = self.client.get(reverse('accounts:profile'))
        # Assigned staff labels
        self.assertContains(resp, 'Doctor:')
        self.assertContains(resp, self.doctor.username)
        self.assertContains(resp, 'Caregiver:')
        self.assertContains(resp, self.caregiver.username)
        # Alzheimer duration displayed
        self.assertContains(resp, 'Alzheimer')
        self.assertContains(resp, '3 year')

    def test_mark_reminder_read(self):
        self.client.login(username='patient1', password='pass')
        url = reverse('accounts:reminder_mark_read', args=[self.reminder.id])
        resp = self.client.get(url, follow=True)
        self.reminder.refresh_from_db()
        self.assertTrue(self.reminder.read)
