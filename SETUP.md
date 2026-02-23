# MemoryCare - Quick Setup Guide

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] MySQL Server installed and running
- [ ] pip installed
- [ ] Virtual environment tool (venv) available

## Step-by-Step Setup

### 1. Database Setup

First, create the MySQL database:

```sql
CREATE DATABASE memorycare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or using MySQL command line:
```bash
mysql -u root -p
CREATE DATABASE memorycare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
SECRET_KEY=django-insecure-change-this-to-a-random-secret-key-in-production
DEBUG=True
DB_NAME=memorycare_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

**Important**: Replace `your_mysql_password` with your actual MySQL root password.

### 3. Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

**If mysqlclient installation fails**, use this alternative:

```bash
# Install pymysql instead
pip install pymysql

# Then edit memorycare/__init__.py and add:
import pymysql
pymysql.install_as_MySQLdb()
```

### 5. Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 6. Create Admin User (Doctor)

```bash
python manage.py createsuperuser
```

Enter:
- Username: (choose a username)
- Email: (your email)
- Password: (choose a strong password)

**After creating the superuser**, you need to set the role to 'DOCTOR':

1. Start the server: `python manage.py runserver`
2. Go to `http://127.0.0.1:8000/admin/`
3. Login with your superuser credentials
4. Go to "Users" → Select your user
5. Set "Role" to "Doctor (Admin)"
6. Save

### 7. Run the Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Testing the Setup

1. **Login as Doctor**: Use your superuser credentials
2. **Create a Caregiver**: 
   - Go to "Create User" in navigation
   - Fill the form and select "Caregiver" role
   - Submit
3. **Create a Patient**:
   - Go to "Create User" again
   - Fill the form and select "Patient" role
   - Submit
4. **View All Users**: Click "All Users" to see the list

## Common Issues

### Issue: "No module named 'mysqlclient'"

**Solution**: Install MySQL development libraries or use pymysql (see step 4 above)

### Issue: "Access denied for user"

**Solution**: Check your MySQL credentials in `.env` file

### Issue: "Unknown database 'memorycare_db'"

**Solution**: Create the database first (see step 1)

### Issue: "ModuleNotFoundError: No module named 'decouple'"

**Solution**: Run `pip install python-decouple`

## Next Steps

After successful setup:
1. Explore the admin panel at `/admin/`
2. Test user creation as a Doctor
3. Test login/logout functionality
4. Explore the API endpoints at `/api/users/`

## API Testing

You can test the API using:
- Browser (for GET requests when logged in)
- Postman
- curl commands
- Python requests library

Example API call (when logged in):
```bash
curl http://127.0.0.1:8000/api/users/me/
```
