from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Populate empty first_name/last_name for users from their username (safe default).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
        parser.add_argument('--role', type=str, default='', help='Restrict to users with ROLE value (e.g. PATIENT)')

    def handle(self, *args, **options):
        from accounts.models import User

        dry_run = options.get('dry_run')
        role = options.get('role')

        qs = User.objects.all()
        if role:
            qs = qs.filter(role=role)
        # Import models for Q lookups
        from django.db import models

        targets = qs.filter(models.Q(first_name='') | models.Q(first_name__isnull=True) | models.Q(last_name='') | models.Q(last_name__isnull=True))

        if not targets.exists():
            self.stdout.write(self.style.SUCCESS('No users with empty first_name/last_name found.'))
            return

        self.stdout.write(f'Found {targets.count()} users with missing names.')

        changes = []
        for u in targets:
            uname = (u.username or '').strip()
            if not uname:
                continue
            # Try to split username on common separators
            parts = None
            for sep in (' ', '.', '_', '-'):
                if sep in uname:
                    parts = [p for p in uname.split(sep) if p]
                    break

            if parts and len(parts) >= 2:
                first = parts[0].title()
                last = ' '.join(parts[1:]).title()
            else:
                # Single token username: put it into first_name (titlecased)
                first = uname.replace('_', ' ').replace('.', ' ').title()
                last = ''

            new_first = u.first_name if u.first_name else first
            new_last = u.last_name if u.last_name else last

            if (new_first != (u.first_name or '')) or (new_last != (u.last_name or '')):
                changes.append((u.id, u.username, u.first_name, u.last_name, new_first, new_last))

        if not changes:
            self.stdout.write(self.style.SUCCESS('No changes required.'))
            return

        # Report
        for ch in changes:
            uid, username, old_first, old_last, new_first, new_last = ch
            self.stdout.write(f'User {uid} ({username}): "{old_first}" "{old_last}" -> "{new_first}" "{new_last}"')

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run enabled; no changes applied.'))
            return

        # Apply
        with transaction.atomic():
            from accounts.models import User as UModel
            for uid, username, old_first, old_last, new_first, new_last in changes:
                u = UModel.objects.get(id=uid)
                u.first_name = new_first
                u.last_name = new_last
                u.save()

        self.stdout.write(self.style.SUCCESS(f'Applied changes to {len(changes)} users.'))
