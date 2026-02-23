# How to Run MemoryCare Project

## 🚀 Step-by-Step Instructions

### Prerequisites Check
- ✅ Python 3.8+ (You have Python 3.14.0)
- ⚠️ MySQL Server (needs to be installed and running)
- ⚠️ Virtual environment (will create)

---

## Step 1: Create MySQL Database

**Option A: Using MySQL Command Line**
```bash
mysql -u root -p
```
Then run:
```sql
CREATE DATABASE memorycare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**Option B: Using MySQL Workbench or phpMyAdmin**
- Create a new database named `memorycare_db`
- Set character set to `utf8mb4`
- Set collation to `utf8mb4_unicode_ci`

---

## Step 2: Create Environment File (.env)

Create a file named `.env` in the project root directory with this content:

```env
SECRET_KEY=django-insecure-change-this-to-a-random-secret-key-in-production-12345
DEBUG=True
DB_NAME=memorycare_db
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_HOST=localhost
DB_PORT=3306
```

**Important**: Replace `your_mysql_password_here` with your actual MySQL root password.

---

## Step 3: Create Virtual Environment

```bash
python -m venv venv
```

**Activate Virtual Environment:**
- **Windows (PowerShell/CMD):**
  ```bash
  venv\Scripts\activate
  ```
- **Windows (Git Bash):**
  ```bash
  source venv/Scripts/activate
  ```
- **Linux/Mac:**
  ```bash
  source venv/bin/activate
  ```

You should see `(venv)` at the beginning of your command prompt.

---

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you get MySQL client errors**, use this alternative:

```bash
pip install pymysql
```

Then edit `memorycare/__init__.py` and add at the top:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 5: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all the database tables.

---

## Step 6: Create Admin User (Doctor)

**Option A: Using createsuperuser**
```bash
python manage.py createsuperuser
```
Enter:
- Username: (choose any username)
- Email: (your email)
- Password: (choose a strong password)

**Then set role to Doctor:**
1. Start server: `python manage.py runserver`
2. Go to http://127.0.0.1:8000/admin/
3. Login with your superuser credentials
4. Go to "Users" → Click on your username
5. Set "Role" to "Doctor (Admin)"
6. Click "Save"

**Option B: Using create_doctor command (Recommended)**
```bash
python manage.py create_doctor
```
This creates a doctor user directly with the DOCTOR role.

---

## Step 7: Run the Development Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## Step 8: Access the Application

Open your web browser and visit:

- **Login Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Endpoints**: http://127.0.0.1:8000/api/users/

---

## 🎯 Quick Test

1. **Login** with your doctor account
2. You should see the **Doctor Dashboard** with statistics
3. Click **"Create User"** to create a caregiver or patient
4. Click **"All Users"** to see the list of users
5. Test **logout** and **login** again

---

## ⚠️ Troubleshooting

### Error: "No module named 'mysqlclient'"
**Solution**: Install pymysql instead:
```bash
pip install pymysql
```
Then add to `memorycare/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Error: "Access denied for user"
**Solution**: Check your MySQL password in `.env` file

### Error: "Unknown database 'memorycare_db'"
**Solution**: Create the database first (Step 1)

### Error: "ModuleNotFoundError: No module named 'decouple'"
**Solution**: 
```bash
pip install python-decouple
```

### Error: "django.core.exceptions.ImproperlyConfigured"
**Solution**: Make sure `.env` file exists in project root

---

## 📝 Quick Command Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create doctor user
python manage.py create_doctor

# Run server
python manage.py runserver

# Stop server
CTRL+C (or CTRL+BREAK on Windows)
```

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ Server starts without errors
- ✅ You can access http://127.0.0.1:8000/
- ✅ Login page loads
- ✅ You can login with your doctor account
- ✅ Dashboard displays correctly
- ✅ You can create new users

---

**Need help?** Check the other documentation files:
- `SETUP.md` - Detailed setup guide
- `README.md` - Full project documentation
- `QUICK_START.md` - Quick reference
