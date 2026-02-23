import os
import django
from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memorycare.settings')
django.setup()

User = get_user_model()
client = Client()

def verify_admin_access():
    print("--- Verifying Admin Access ---")
    
    # 1. Setup Data
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@test.com'})
    admin_user.set_password('Password123!')
    admin_user.role = 'DOCTOR'
    admin_user.is_superuser = True
    admin_user.save()
    
    patient_user, _ = User.objects.get_or_create(username='patient_test', defaults={'email': 'patient@test.com'})
    patient_user.set_password('Password123!')
    patient_user.role = 'PATIENT'
    patient_user.save()

    # 2. Test Admin Login
    print(f"Attempting login for {admin_user.username}...")
    login_success = client.login(username='admin', password='Password123!')
    if login_success:
        print("PASS: Admin login successful.")
    else:
        print("FAIL: Admin login failed.")
        return

    # 3. Test Redirect/Dashboard Access
    response = client.get(reverse('dashboard:home'))
    if response.status_code == 302 and response.url == reverse('dashboard:doctor_dashboard'):
        print(f"PASS: Admin redirected to {response.url}")
    else:
        print(f"FAIL: Admin redirect incorrect. Status: {response.status_code}, URL: {getattr(response, 'url', 'N/A')}")

    response = client.get(reverse('dashboard:doctor_dashboard'))
    if response.status_code == 200:
        print("PASS: Admin can access Doctor Dashboard.")
    else:
        print(f"FAIL: Admin cannot access Doctor Dashboard. Status: {response.status_code}")

    # 4. Test Patient Access (Should be blocked)
    client.logout()
    client.login(username='patient_test', password='Password123!')
    response = client.get(reverse('dashboard:doctor_dashboard'))
    # Expect redirect or error
    if response.status_code == 302:
        print(f"PASS: Patient denied access to Admin Dashboard (Redirected to {response.url}).")
    elif response.status_code == 403:
        print("PASS: Patient denied access (403).")
    else:
        print(f"FAIL: Patient accessed Admin Dashboard! Status: {response.status_code}")

if __name__ == '__main__':
    verify_admin_access()
