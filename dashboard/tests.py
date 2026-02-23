from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import User, Reminder


class PatientDashboardTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='p1', password='pass', role='PATIENT', email='p1@example.com')
        # today's reminder
        Reminder.objects.create(patient=self.patient, title='Test Today', message='do task', scheduled_for=timezone.now())

    def test_dashboard_tasks_and_overview(self):
        self.client.login(username='p1', password='pass')
        resp = self.client.get(reverse('dashboard:patient_dashboard'))
        self.assertEqual(resp.status_code, 200)
        # Check that schedule section appears and today's reminder is shown
        self.assertContains(resp, "Today's Schedule")
        self.assertContains(resp, 'Test Today')

    def test_dashboard_includes_activity_counts_and_health_label(self):
        from .models import DailyActivity
        import datetime
        # add two activities for today, one completed
        now = timezone.now()
        a1 = DailyActivity.objects.create(user=self.patient, name='A1', activity_type='exercise', scheduled_for=now)
        a2 = DailyActivity.objects.create(user=self.patient, name='A2', activity_type='exercise', scheduled_for=now)
        a2.completed = True
        a2.save()
        self.client.login(username='p1', password='pass')
        resp = self.client.get(reverse('dashboard:patient_dashboard'))
        self.assertEqual(resp.status_code, 200)
        # context should have counts and label
        self.assertIn('total_activities', resp.context)
        self.assertIn('completed_activities', resp.context)
        self.assertIn('remaining_activities', resp.context)
        self.assertIn('health_label', resp.context)
        self.assertEqual(resp.context['total_activities'], 2)
        self.assertEqual(resp.context['completed_activities'], 1)
        self.assertEqual(resp.context['remaining_activities'], 1)


class DashboardFeatureTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='pint', password='pass', role='PATIENT', email='pint@example.com')

    def test_take_test_and_view_result(self):
        from .models import CognitiveTest, TestResult
        # Create a test
        t = CognitiveTest.objects.create(name='T1', description='desc', questions=[{'text':'Q1','choices':['A','B'],'answer':'B'}])
        self.client.login(username='pint', password='pass')
        # GET form
        resp = self.client.get(reverse('dashboard:take_test', args=[t.id]))
        self.assertEqual(resp.status_code, 200)
        # Submit an answer (old flow)
        resp = self.client.post(reverse('dashboard:take_test', args=[t.id]), {'q0': 'B'})
        self.assertEqual(resp.status_code, 302)
        result = TestResult.objects.filter(user=self.patient, test=t).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 1)

    def test_ajax_test_flow(self):
        from .models import CognitiveTest, TestResult
        t = CognitiveTest.objects.create(name='T2', description='desc', questions=[{'text':'Q1','choices':['A','B'],'answer':'B'},{'text':'Q2','choices':['X','Y'],'answer':'Y'}])
        self.client.login(username='pint', password='pass')
        # load first question
        resp = self.client.get(reverse('dashboard:test_ajax_question', args=[t.id]) + '?q=0')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        # post answer to get next question
        resp = self.client.post(reverse('dashboard:test_ajax_answer', args=[t.id]), {'idx': 0, 'answer': 'B'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data.get('finished'))
        # post second answer to finish
        resp = self.client.post(reverse('dashboard:test_ajax_answer', args=[t.id]), {'idx': 1, 'answer': 'Y'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('finished'))
        result = TestResult.objects.filter(user=self.patient, test=t).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 2)

    def test_mood_submission_and_list(self):
        from .models import MoodEntry
        self.client.login(username='pint', password='pass')
        resp = self.client.post(reverse('dashboard:mood'), {'mood':'happy','note':'Feeling good'})
        self.assertEqual(resp.status_code, 302)
        entry = MoodEntry.objects.filter(user=self.patient).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.get_mood_display(), 'Happy')

    def test_quick_mood_button(self):
        from .models import MoodEntry
        self.client.login(username='pint', password='pass')
        resp = self.client.post(reverse('dashboard:mood'), {'mood': 'neutral'})
        self.assertEqual(resp.status_code, 302)
        entry = MoodEntry.objects.filter(user=self.patient).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.get_mood_display(), 'Neutral')

    def test_daily_activities_flow(self):
        from .models import DailyActivity
        import datetime
        self.client.login(username='pint', password='pass')
        # create an activity for today
        now = timezone.now()
        a = DailyActivity.objects.create(user=self.patient, name='Memory Exercise', activity_type='exercise', scheduled_for=now)
        # Access daily activities page
        resp = self.client.get(reverse('dashboard:daily_activities'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Memory Exercise')
        # Toggle completion
        resp = self.client.post(reverse('dashboard:toggle_activity', args=[a.id]), {'next': reverse('dashboard:daily_activities')})
        self.assertEqual(resp.status_code, 302)
        a.refresh_from_db()
        self.assertTrue(a.completed)
        # Toggle back to incomplete
        resp = self.client.post(reverse('dashboard:toggle_activity', args=[a.id]), {'next': reverse('dashboard:daily_activities')})
        a.refresh_from_db()
        self.assertFalse(a.completed)

    def test_patient_creates_activity_for_self(self):
        from .models import DailyActivity
        self.client.login(username='pint', password='pass')
        now = timezone.now().replace(microsecond=0)
        resp = self.client.post(reverse('dashboard:activity_create'), {
            'name': 'Self Walk', 'activity_type': 'exercise', 'scheduled_for': now.strftime('%Y-%m-%dT%H:%M'), 'recurrence': 'none', 'recurrence_interval': 1
        })
        self.assertEqual(resp.status_code, 302)
        a = DailyActivity.objects.filter(user=self.patient, name='Self Walk').first()
        self.assertIsNotNone(a)

    def test_staff_creates_activity_for_patient(self):
        from .models import DailyActivity
        # create a caregiver
        cg = User.objects.create_user(username='cg1', password='pass', role='CAREGIVER', email='cg1@example.com')
        self.client.login(username='cg1', password='pass')
        now = timezone.now().replace(microsecond=0)
        resp = self.client.post(reverse('dashboard:activity_create'), {
            'user': self.patient.id, 'name': 'Caregiver Walk', 'activity_type': 'exercise', 'scheduled_for': now.strftime('%Y-%m-%dT%H:%M'), 'recurrence': 'none', 'recurrence_interval': 1
        })
        self.assertEqual(resp.status_code, 302)
        a = DailyActivity.objects.filter(user=self.patient, name='Caregiver Walk').first()
        self.assertIsNotNone(a)

    def test_toggle_activity_ajax(self):
        from .models import DailyActivity
        self.client.login(username='pint', password='pass')
        now = timezone.now()
        a = DailyActivity.objects.create(user=self.patient, name='Walk AJAX', activity_type='exercise', scheduled_for=now)
        resp = self.client.post(reverse('dashboard:toggle_activity_ajax', args=[a.id]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertTrue(data.get('completed'))
        a.refresh_from_db()
        self.assertTrue(a.completed)

    def test_patient_creates_reminder_via_ajax(self):
        self.client.login(username='pint', password='pass')
        # create a reminder
        from django.utils import timezone
        dt = timezone.now().replace(microsecond=0)
        scheduled = dt.strftime('%Y-%m-%dT%H:%M:%S')
        resp = self.client.post(reverse('accounts:reminder_create_ajax'), {'title': 'Take Meds', 'message': 'Take morning medicine', 'scheduled_for': scheduled})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        # now fetch dashboard data and ensure reminder is included
        resp = self.client.get(reverse('dashboard:patient_dashboard_data_ajax'))
        self.assertEqual(resp.status_code, 200)
        d = resp.json()
        self.assertTrue(any(r.get('title') == 'Take Meds' for r in d.get('reminders', [])))
        # health components and schedule exist
        self.assertIn('health_components', d)
        self.assertIn('schedule', d)
        self.assertIsInstance(d.get('schedule'), list)
    def test_recurring_activity_shows_today(self):
        from .models import DailyActivity
        import datetime
        self.client.login(username='pint', password='pass')
        yesterday = timezone.now() - datetime.timedelta(days=1)
        a = DailyActivity.objects.create(user=self.patient, name='Daily Walk', activity_type='exercise', scheduled_for=yesterday, recurrence='daily', recurrence_interval=1)
        resp = self.client.get(reverse('dashboard:daily_activities'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Daily Walk')

    def test_patient_dashboard_data_ajax(self):
        # ensure that the new dashboard ajax endpoint returns expected keys
        from .models import DailyActivity
        import datetime
        self.client.login(username='pint', password='pass')
        now = timezone.now()
        DailyActivity.objects.create(user=self.patient, name='AJAX Walk', activity_type='exercise', scheduled_for=now)
        resp = self.client.get(reverse('dashboard:patient_dashboard_data_ajax'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertIn('health_score', data)
        self.assertIn('mood', data)
        self.assertIn('cognitive', data)
        self.assertIn('activities', data)

    def test_activity_create_ajax(self):
        from .models import DailyActivity
        self.client.login(username='pint', password='pass')
        now = timezone.now().replace(microsecond=0)
        resp = self.client.post(reverse('dashboard:activity_create_ajax'), {
            'name': 'AJAX Created', 'activity_type': 'exercise', 'scheduled_for': now.strftime('%Y-%m-%dT%H:%M'), 'recurrence': 'none', 'recurrence_interval': 1
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        a = DailyActivity.objects.filter(user=self.patient, name='AJAX Created').first()
        self.assertIsNotNone(a)

    def test_schedule_order_and_components(self):
        # Ensure schedule is merged and sorted, and health components are present
        from .models import DailyActivity
        from accounts.models import Reminder
        import datetime
        self.client.login(username='pint', password='pass')
        now = timezone.now().replace(microsecond=0)
        r1 = Reminder.objects.create(patient=self.patient, title='Med A', message='Take A', scheduled_for=now + datetime.timedelta(hours=1))
        r2 = Reminder.objects.create(patient=self.patient, title='Med B', message='Take B', scheduled_for=now + datetime.timedelta(hours=4))
        a1 = DailyActivity.objects.create(user=self.patient, name='Walk', activity_type='exercise', scheduled_for=now + datetime.timedelta(hours=2))
        a2 = DailyActivity.objects.create(user=self.patient, name='Take pill', activity_type='medication', scheduled_for=now + datetime.timedelta(hours=3), completed=True)
        resp = self.client.get(reverse('dashboard:patient_dashboard_data_ajax'))
        self.assertEqual(resp.status_code, 200)
        d = resp.json()
        sched = d.get('schedule', [])
        self.assertGreaterEqual(len(sched), 4)
        # first scheduled item should be 'Med A'
        self.assertEqual(sched[0].get('title'), 'Med A')
        # health components exist
        hc = d.get('health_components')
        self.assertIn('medication', hc)
        self.assertIn('exercise', hc)
        self.assertIn('cognitive', hc)
        self.assertIn('sleep', hc)
        self.assertIn('social', hc)

