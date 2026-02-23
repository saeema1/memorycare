# 🎯 Complete Setup Guide - MemoryCare Phase 1

## ✅ Phase 1 Status: COMPLETE

All Phase 1 requirements have been implemented and fixed. Follow these steps to run the project.

---

## 🚀 Quick Start (Easiest Method)

### Option 1: Use the Batch File (Windows)
1. **Double-click** `START_SERVER.bat`
2. Wait for the server to start
3. Open browser to: http://127.0.0.1:8000/

### Option 2: Manual PowerShell Commands

Open PowerShell in the project directory and run:

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Set SQLite mode (works without MySQL)
$env:USE_SQLITE = "True"

# 3. Run migrations (if not done already)
python manage.py migrate

# 4. Create doctor user (if not done already)
python manage.py create_doctor

# 5. Start server
python manage.py runserver
```

---

## 📋 Detailed Step-by-Step Instructions

### Step 1: Verify Virtual Environment

Make sure you're in the project directory and activate venv:

```powershell
cd "C:\Users\user\OneDrive\Desktop\memorycare"
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your prompt.

### Step 2: Install Dependencies (if needed)

```powershell
python -m pip install -r requirements.txt
```

### Step 3: Set Database Mode

**For SQLite (Easiest - No MySQL needed):**
```powershell
$env:USE_SQLITE = "True"
```

**For MySQL (if you have MySQL running):**
```powershell
$env:USE_SQLITE = "False"
# Make sure .env file has correct MySQL credentials
```

### Step 4: Run Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin User (Doctor)

```powershell
python manage.py create_doctor
```

Follow prompts or use:
```powershell
python manage.py create_doctor --username admin --email admin@example.com --password AdminPass123! --first-name Admin --last-name User
```

**Default credentials created:**
- Username: `admin`
- Password: `AdminPass123!`

### Step 6: Start the Server

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 7: Access the Application

Open your browser and go to:
- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 🎯 Test Phase 1 Features

### 1. Login as Doctor
- Go to http://127.0.0.1:8000/
- Login with: `admin` / `AdminPass123!`
- You should see the Doctor Dashboard

### 2. Create a Caregiver
- Click "Create User" in navigation
- Fill the form
- Select "Caregiver" role
- Submit

### 3. Create a Patient
- Click "Create User" again
- Fill the form
- Select "Patient" role
- Submit

### 4. View All Users
- Click "All Users" in navigation
- You should see all registered users

### 5. Test Admin Panel
- Go to http://127.0.0.1:8000/admin/
- Login with same credentials
- Manage users from admin interface

### 6. Test API
- While logged in, visit: http://127.0.0.1:8000/api/users/me/
- Should see your user profile in JSON format

---

## ⚠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pymysql'"
**Solution:** Make sure virtual environment is activated:
```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Error: "Can't connect to MySQL server"
**Solution:** Use SQLite instead:
```powershell
$env:USE_SQLITE = "True"
python manage.py migrate
python manage.py runserver
```

### Error: "AttributeError: 'function' object has no attribute 'as_view'"
**Solution:** Already fixed! Make sure you have the latest code.

### Error: "ERR_CONNECTION_REFUSED" in browser
**Solution:** Make sure the server is running:
```powershell
python manage.py runserver
```
Wait for "Starting development server..." message.

### Server won't start
**Solution:** Check if port 8000 is in use:
```powershell
# Try a different port
python manage.py runserver 8001
```
Then access: http://127.0.0.1:8001/

---

## ✅ Phase 1 Checklist

All these features are implemented and working:

- [x] Django backend project
- [x] Database (SQLite or MySQL)
- [x] Custom User model with 3 roles
- [x] User registration
- [x] User login/logout
- [x] Role-based access control
- [x] Doctor can create users
- [x] Doctor can view all users
- [x] Separate dashboards for each role
- [x] Django Admin Panel
- [x] REST API endpoints
- [x] Modern UI templates

---

## 📝 Quick Command Reference

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Use SQLite
$env:USE_SQLITE = "True"

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create doctor
python manage.py create_doctor

# Run server
python manage.py runserver

# Stop server
Press CTRL+C
```

---

## 🎉 Success!

Once the server is running and you can access http://127.0.0.1:8000/, **Phase 1 is complete!**

You can now:
- ✅ Login as Doctor
- ✅ Create Caregiver and Patient accounts
- ✅ View all users
- ✅ Access admin panel
- ✅ Test API endpoints
- ✅ Use role-based dashboards

**Phase 1 is fully functional and ready for use!** 🚀
