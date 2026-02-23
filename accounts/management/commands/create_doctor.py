"""
Management command to create a doctor user
Usage: python manage.py create_doctor
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a doctor (admin) user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the doctor')
        parser.add_argument('--email', type=str, help='Email for the doctor')
        parser.add_argument('--password', type=str, help='Password for the doctor')
        parser.add_argument('--first-name', type=str, default='', help='First name')
        parser.add_argument('--last-name', type=str, default='', help='Last name')

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')

        if not username:
            username = input('Username: ')
        if not email:
            email = input('Email: ')
        if not password:
            from getpass import getpass
            password = getpass('Password: ')
            password_confirm = getpass('Password (again): ')
            if password != password_confirm:
                self.stdout.write(self.style.ERROR('Passwords do not match!'))
                return

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='DOCTOR',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created doctor user: {username}')
            )
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" already exists!')
            )
