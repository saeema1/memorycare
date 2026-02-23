# 🚀 How to Run MemoryCare Project

## Quick Start (Windows)

### Option 1: Use the Automated Script
1. Double-click `run_project.bat`
2. Follow the on-screen instructions
3. The script will guide you through setup

### Option 2: Manual Setup (Recommended for Learning)

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8+ installed (You have Python 3.14.0 ✅)
- ✅ MySQL Server installed and running
- ✅ MySQL root password

---

## Step-by-Step Instructions

### Step 1: Create MySQL Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE memorycare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

### Step 2: Create .env File

Create a file named `.env` in the project root with this content:

```env
SECRET_KEY=django-insecure-change-this-in-production-12345
DEBUG=True
DB_NAME=memorycare_db
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=3306
```

**Replace `YOUR_MYSQL_PASSWORD_HERE` with your actual MySQL password!**

---

### Step 3: Create Virtual Environment

Open PowerShell or Command Prompt in the project directory and run:

```bash
python -m venv venv
```

---

### Step 4: Activate Virtual Environment

**In PowerShell/CMD:**
```bash
venv\Scripts\activate
```

You should see `(venv)` at the start of your command prompt.

---

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you get MySQL errors**, use this instead:
```bash
pip install pymysql
```

Then edit `memorycare/__init__.py` and add at the top:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

### Step 6: Create Database Tables

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Step 7: Create Admin User (Doctor)

**Recommended method:**
```bash
python manage.py create_doctor
```

Follow the prompts to create your doctor account.

**Alternative method:**
```bash
python manage.py createsuperuser
```
Then go to http://127.0.0.1:8000/admin/ and set role to "Doctor (Admin)".

---

### Step 8: Run the Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

### Step 9: Open in Browser

Open your web browser and go to:
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 🎯 Test the Application

1. **Login** with your doctor account
2. You should see the **Doctor Dashboard**
3. Click **"Create User"** to create a caregiver or patient
4. Click **"All Users"** to see all registered users
5. Test the **Admin Panel** at `/admin/`

---

## ⚠️ Common Issues & Solutions

### Issue 1: "No module named 'mysqlclient'"
**Solution:**
```bash
pip install pymysql
```
Then add to `memorycare/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

### Issue 2: "Access denied for user"
**Solution:** Check your MySQL password in the `.env` file

### Issue 3: "Unknown database 'memorycare_db'"
**Solution:** Create the database first (Step 1)

### Issue 4: "ModuleNotFoundError: No module named 'decouple'"
**Solution:**
```bash
pip install python-decouple
```

### Issue 5: Virtual environment not activating
**Solution:** Make sure you're in the project directory and run:
```bash
.\venv\Scripts\activate
```

---

## 📝 Quick Command Cheat Sheet

```bash
# Activate virtual environment
venv\Scripts\activate

# Install packages
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
Press CTRL+C
```

---

## ✅ Success Checklist

You'll know everything works when:
- ✅ Server starts without errors
- ✅ You can access http://127.0.0.1:8000/
- ✅ Login page loads correctly
- ✅ You can login with your doctor account
- ✅ Dashboard shows statistics
- ✅ You can create new users

---

## 🆘 Need Help?

- Check `SETUP.md` for detailed setup instructions
- Check `README.md` for full project documentation
- Check `HOW_TO_RUN.md` for alternative instructions

---

## 🎉 You're Ready!

Once the server is running, you can:
- Login as Doctor and manage users
- Create Caregiver and Patient accounts
- View all users in the system
- Access the Django Admin Panel
- Test the REST API endpoints

**Happy coding!** 🚀
