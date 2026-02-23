import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memorycare.settings')
django.setup()

from accounts.models import User

def create_admin():
    username = 'admin'
    email = 'admin@memorycare.com'
    password = 'Password123!'
    role = 'DOCTOR'

    if not User.objects.filter(username=username).exists():
        print(f"Creating default admin user: {username}")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = "System"
        user.last_name = "Admin"
        user.role = role
        user.is_staff = True # Optional: gives access to Django Admin panel too
        user.is_superuser = True # Optional
        user.save()
        print("Admin user created successfully.")
    else:
        print(f"User '{username}' already exists. Updating role/password...")
        user = User.objects.get(username=username)
        user.role = role
        user.set_password(password)
        user.save()
        print("Admin user updated successfully.")

if __name__ == '__main__':
    create_admin()
