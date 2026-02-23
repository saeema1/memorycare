# MemoryCare Project Structure

## Directory Overview

```
memorycare/
│
├── memorycare/                 # Main Django project package
│   ├── __init__.py            # Package initialization
│   ├── settings.py            # Django settings and configuration
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI configuration for deployment
│   └── asgi.py                # ASGI configuration for async support
│
├── accounts/                   # User management application
│   ├── __init__.py
│   ├── admin.py               # Django admin configuration for User model
│   ├── apps.py                # App configuration
│   ├── models.py              # Custom User model with roles
│   ├── views.py               # Authentication and user management views
│   ├── forms.py               # User registration and login forms
│   ├── urls.py                # URL patterns for accounts app
│   ├── api_views.py           # REST API viewsets
│   ├── serializers.py         # DRF serializers for User model
│   ├── api_urls.py            # API URL patterns
│   └── management/
│       └── commands/
│           └── create_doctor.py  # Management command to create doctor
│
├── dashboard/                  # Dashboard application
│   ├── __init__.py
│   ├── apps.py                # App configuration
│   ├── views.py               # Role-based dashboard views
│   └── urls.py                # Dashboard URL patterns
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template with navigation
│   ├── accounts/
│   │   ├── login.html         # Login page
│   │   ├── register.html      # Registration page
│   │   ├── create_user.html   # Doctor: Create user page
│   │   └── user_list.html     # Doctor: List all users
│   └── dashboard/
│       ├── home.html          # Home/redirect page
│       ├── doctor_dashboard.html    # Doctor dashboard
│       ├── caregiver_dashboard.html # Caregiver dashboard
│       └── patient_dashboard.html   # Patient dashboard
│
├── static/                     # Static files (CSS, JS, images)
│   └── .gitkeep
│
├── manage.py                   # Django management script
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # Main project documentation
├── SETUP.md                   # Setup instructions
└── PROJECT_STRUCTURE.md       # This file

```

## Application Breakdown

### memorycare (Main Project)
- **Purpose**: Main Django project configuration
- **Key Files**:
  - `settings.py`: Database, installed apps, middleware, static files configuration
  - `urls.py`: Root URL routing

### accounts (User Management)
- **Purpose**: Handles all user-related functionality
- **Models**:
  - `User`: Custom user model extending AbstractUser with role-based fields
- **Views**:
  - `login_view`: User authentication
  - `register_view`: Public user registration
  - `create_user_view`: Doctor-only user creation
  - `UserListView`: Doctor-only user listing
- **API**:
  - `UserViewSet`: REST API for user management
- **Forms**:
  - `UserRegistrationForm`: User registration with role selection
  - `UserLoginForm`: Simple login form

### dashboard (Role-Based Dashboards)
- **Purpose**: Provides role-specific dashboard views
- **Views**:
  - `home`: Redirects to role-specific dashboard
  - `doctor_dashboard`: Admin dashboard with statistics
  - `caregiver_dashboard`: Caregiver-specific dashboard
  - `patient_dashboard`: Patient-specific dashboard

## Database Schema

### User Table
- Extends Django's built-in user fields
- Custom fields:
  - `role`: CharField (DOCTOR, CAREGIVER, PATIENT)
  - `phone_number`: CharField
  - `date_of_birth`: DateField
  - `address`: TextField
  - `emergency_contact_name`: CharField (Patient)
  - `emergency_contact_phone`: CharField (Patient)
  - `specialization`: CharField (Caregiver)
  - `license_number`: CharField (Caregiver)

## URL Patterns

### Root URLs (`memorycare/urls.py`)
- `/admin/` → Django admin panel
- `/` → Accounts URLs
- `/dashboard/` → Dashboard URLs
- `/api/` → API URLs

### Accounts URLs (`accounts/urls.py`)
- `/login/` → Login page
- `/register/` → Registration page
- `/logout/` → Logout
- `/create-user/` → Create user (Doctor only)
- `/users/` → List users (Doctor only)

### Dashboard URLs (`dashboard/urls.py`)
- `/` → Home (redirects to role dashboard)
- `/doctor/` → Doctor dashboard
- `/caregiver/` → Caregiver dashboard
- `/patient/` → Patient dashboard

### API URLs (`accounts/api_urls.py`)
- `/api/users/` → User list/create
- `/api/users/{id}/` → User detail/update/delete
- `/api/users/me/` → Current user profile

## Security Features

1. **Role-Based Access Control**: Decorators and view logic enforce role permissions
2. **Password Hashing**: Django's built-in password hashing
3. **CSRF Protection**: Enabled for all forms
4. **Session Authentication**: Used for web and API access
5. **Admin Permissions**: Only doctors can create/manage users

## Key Design Decisions

1. **Custom User Model**: Extends AbstractUser to add role and additional fields
2. **Separate Apps**: Clear separation between accounts and dashboard
3. **Role-Based Views**: Each role has dedicated dashboard
4. **REST API**: DRF integration for future mobile app support
5. **Template Inheritance**: Base template for consistent UI

## Future Extensibility

The structure is designed to easily add:
- New apps for health data, appointments, etc.
- Additional user roles
- More API endpoints
- Enhanced dashboard features
- Mobile app integration
