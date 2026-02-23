# MemoryCare Web Application - Phase 1

A full-stack web application designed to support Alzheimer's care management. Phase 1 focuses on core system setup and user management.

## Project Overview

MemoryCare is a Django-based web application that provides role-based access control for managing Alzheimer's care. Phase 1 implements the foundation with user authentication, role management, and basic dashboards.

## Features (Phase 1)

- ✅ Django backend with MySQL database
- ✅ Custom user model with three roles: Doctor (Admin), Caregiver, and Patient
- ✅ User registration and authentication system
- ✅ Role-based access control
- ✅ Doctor (Admin) can create and manage caregiver and patient accounts
- ✅ Separate dashboards for each role
- ✅ Django Admin Panel integration
- ✅ Django REST Framework API endpoints

## Technology Stack

- **Backend**: Python 3.8+, Django 4.2.7
- **Database**: MySQL
- **API**: Django REST Framework 3.14.0
- **Frontend**: HTML, CSS (Basic templates)

## Project Structure

```
memorycare/
├── memorycare/          # Main project directory
│   ├── __init__.py
│   ├── settings.py      # Django settings
│   ├── urls.py         # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── accounts/            # User management app
│   ├── models.py       # Custom User model
│   ├── views.py        # Authentication views
│   ├── forms.py        # Registration forms
│   ├── admin.py        # Admin configuration
│   ├── urls.py         # Account URLs
│   ├── api_views.py    # REST API views
│   ├── serializers.py  # API serializers
│   └── api_urls.py     # API URLs
├── dashboard/          # Dashboard app
│   ├── views.py        # Dashboard views
│   └── urls.py         # Dashboard URLs
├── templates/          # HTML templates
│   ├── base.html
│   ├── accounts/
│   └── dashboard/
├── static/            # Static files (CSS, JS, images)
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

### Step 1: Clone/Download the Project

Navigate to the project directory:
```bash
cd memorycare
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues installing `mysqlclient`, you may need to install MySQL development libraries:

- **Windows**: Download MySQL Connector/C from MySQL website or use `pip install mysqlclient` with pre-built wheels
- **Linux**: `sudo apt-get install default-libmysqlclient-dev python3-dev`
- **Mac**: `brew install mysql-client`

Alternatively, you can use `pymysql` as a replacement:
```bash
pip install pymysql
```
Then add to `memorycare/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Step 4: Configure Database

1. Create a MySQL database:
```sql
CREATE DATABASE memorycare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create a `.env` file in the project root (copy from `.env.example`):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=memorycare_db
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306
```

3. Update the database credentials in `.env` file according to your MySQL setup.

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Doctor/Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account. This will be your Doctor (Admin) account.

**Note**: After creating the superuser, you can set the role to 'DOCTOR' in the Django admin panel or directly in the database.

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Access Points

- **Home/Login**: `http://127.0.0.1:8000/`
- **Registration**: `http://127.0.0.1:8000/register/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **API Root**: `http://127.0.0.1:8000/api/`

### User Roles

1. **Doctor (Admin)**
   - Can create and manage caregiver and patient accounts
   - Can view all registered users
   - Has access to Django Admin Panel
   - Full system access

2. **Caregiver**
   - Has access to caregiver dashboard
   - Can view their own profile
   - Limited access (more features in future phases)

3. **Patient**
   - Has access to patient dashboard
   - Can view their own profile
   - Limited access (more features in future phases)

### Creating Users

**As Doctor (Admin)**:
1. Login with your doctor account
2. Navigate to "Create User" from the navigation bar
3. Fill in the form and select role (Caregiver or Patient)
4. Submit to create the account

**Public Registration**:
- Anyone can register, but will be assigned the "Patient" role by default
- Doctors can later change roles via the admin panel

## API Endpoints

The application includes REST API endpoints using Django REST Framework:

- `GET /api/users/` - List all users (Doctor only)
- `GET /api/users/{id}/` - Get user details
- `POST /api/users/` - Create user (Doctor only)
- `PUT /api/users/{id}/` - Update user (Doctor only)
- `DELETE /api/users/{id}/` - Delete user (Doctor only)
- `GET /api/users/me/` - Get current user's profile

**Authentication**: Session-based authentication is used for API access.

## Database Models

### User Model
- Extends Django's AbstractUser
- Fields: username, email, role, phone_number, date_of_birth, address
- Patient-specific: emergency_contact_name, emergency_contact_phone
- Caregiver-specific: specialization, license_number

## Admin Panel

Access the Django Admin Panel at `/admin/` to:
- Manage all users
- View and edit user details
- Change user roles
- Manage system settings

## Development Notes

- The project uses `python-decouple` for environment variable management
- Custom user model requires migrations before creating superuser
- Role-based access is enforced through decorators and view logic
- All passwords are hashed using Django's password hashing system

## Future Phases

Phase 1 focuses on core setup. Future phases will include:
- Health data management
- Patient-caregiver relationships
- Medical records
- Appointment scheduling
- AI/ML features for Alzheimer's care support

## Troubleshooting

### MySQL Connection Issues
- Verify MySQL server is running
- Check database credentials in `.env`
- Ensure database exists
- Check MySQL user permissions

### Migration Issues
- Delete migration files (except `__init__.py`) and run `makemigrations` again
- Ensure database is accessible

### Static Files Not Loading
- Run `python manage.py collectstatic` (for production)
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings.py

## License

This project is for academic/educational purposes.

## Contact

For questions or issues, please refer to the project documentation or contact the development team.
