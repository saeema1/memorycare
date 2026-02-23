# MemoryCare Quick Reference Guide

## 🚀 Quick Start Commands

### 1️⃣ Open PowerShell
```powershell
cd "C:\Users\user\OneDrive\Desktop\memorycare"
```

### 2️⃣ Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
✅ You should see `(venv)` in your prompt

### 3️⃣ Install Dependencies (First Time Only)
```powershell
python -m pip install -r requirements.txt
```

### 4️⃣ Use SQLite (No MySQL Setup Needed)
```powershell
$env:USE_SQLITE = "True"
```

### 5️⃣ Create Database (First Time Only)
```powershell
python manage.py migrate
```

### 6️⃣ Create Admin User (First Time Only)
```powershell
python manage.py create_doctor
```
Or with parameters:
```powershell
python manage.py create_doctor --username admin --email admin@example.com --password AdminPass123! --first-name Admin --last-name User
```

### 7️⃣ Start Server
```powershell
python manage.py runserver
```

### 8️⃣ Access the Application
- **Login/Home**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API**: http://127.0.0.1:8000/api/users/

---

## 📋 User Credentials (After Setup)

### Admin User (Doctor)
- **Username**: admin
- **Email**: admin@example.com
- **Password**: AdminPass123!
- **Role**: Doctor (Admin)
- **Access**: Full system access

### Create Test Users
1. Login as admin
2. Click "Register" on home page
3. Select role (Patient/Caregiver)
4. Fill in details
5. Submit form

Or use admin panel to create users directly.

---

## 🎯 Main Features

### For Patients
1. **Login** → Enter username/password
2. **Dashboard** → See health score and today's schedule
3. **Cognitive Tests** → Click on test card to take tests
4. **Daily Activities** → View and complete daily tasks
5. **Track Mood** → Click mood buttons to log emotions
6. **View Reminders** → Check scheduled reminders

### For Caregivers
1. **Login** → Enter credentials
2. **Dashboard** → See assigned patients
3. **Patient Details** → Click patient name to view details
4. **Test Results** → Monitor cognitive test scores
5. **Alerts** → View active alerts for patients

### For Doctors/Admin
1. **Login** → Enter admin credentials
2. **Admin Dashboard** → View system statistics
3. **Manage Users** → Create/edit patient and caregiver accounts
4. **Assign Caregivers** → Link caregivers to patients
5. **Django Admin** → Full system management at `/admin/`

---

## 📊 URL Map

| Feature | URL |
|---------|-----|
| Login | http://127.0.0.1:8000/ |
| Register | http://127.0.0.1:8000/accounts/register/ |
| Admin Panel | http://127.0.0.1:8000/admin/ |
| Doctor Dashboard | http://127.0.0.1:8000/dashboard/doctor/ |
| Caregiver Dashboard | http://127.0.0.1:8000/dashboard/caregiver/ |
| Patient Dashboard | http://127.0.0.1:8000/dashboard/patient/ |
| Cognitive Tests | http://127.0.0.1:8000/dashboard/cognitive-tests/ |
| Daily Activities | http://127.0.0.1:8000/dashboard/daily-activities/ |
| Mood Tracking | http://127.0.0.1:8000/dashboard/mood/ |
| User Profile | http://127.0.0.1:8000/accounts/profile/ |
| Edit Profile | http://127.0.0.1:8000/accounts/profile-edit/ |
| Reminders | http://127.0.0.1:8000/accounts/reminders/ |
| API Users | http://127.0.0.1:8000/api/users/ |
| Logout | http://127.0.0.1:8000/accounts/logout/ |

---

## 🧪 Test the Application

### Test Login (Patient)
1. Start server: `python manage.py runserver`
2. Visit: http://127.0.0.1:8000/
3. Register as Patient (if no account exists)
4. Login with patient credentials
5. Should see patient dashboard

### Test Login (Admin)
1. Visit: http://127.0.0.1:8000/admin/
2. Login with admin credentials (created in setup)
3. Should see Django admin interface

### Test CSRF Protection
1. Disable JavaScript
2. Try to submit login form
3. Should get CSRF error (expected, proves protection is active)
4. Enable JavaScript and clear cookies
5. Form should submit successfully

### Test Role-Based Access
1. Login as Patient
2. Try to access `/dashboard/doctor/`
3. Should be redirected to patient dashboard
4. Login as Doctor
5. Should see doctor dashboard

---

## 🛠️ Common Operations

### Create New Patient Account (as Admin)
```powershell
python manage.py create_doctor --role PATIENT --username john_doe --email john@example.com
```
Or use the web interface:
1. Login as admin
2. Click "Add Patient" button
3. Fill form and submit

### Create Cognitive Test (as Admin)
1. Go to Django Admin: `/admin/`
2. Navigate to "Cognitive tests"
3. Click "Add Cognitive Test"
4. Fill name, description, and questions (JSON format)
5. Save

### Assign Caregiver to Patient (as Admin)
1. Go to Doctor Dashboard
2. Find patient in table
3. Select caregiver from dropdown
4. Click "Update"
5. Caregiver is now assigned

### View Patient Results (as Caregiver)
1. Go to Caregiver Dashboard
2. Click patient name in "Your Patients"
3. See test results, activities, mood history
4. View patient details

---

## ⚠️ Troubleshooting

### "Port 8000 already in use"
```powershell
python manage.py runserver 8001
# Or kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Database locked" error
```powershell
# Delete database and restart
del db.sqlite3
python manage.py migrate
```

### "No module named 'django'"
```powershell
pip install -r requirements.txt
```

### "CSRF verification failed"
1. Clear browser cookies
2. Disable browser extensions
3. Use incognito window
4. Check that cookies are enabled

### Virtual environment not activating
```powershell
# Try this if Activate.ps1 fails
# (Run as Administrator first)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

---

## 📱 Demo Data

### Pre-seeded Activities (Patient)
- Morning Medication @ 8:00 AM
- Breakfast @ 8:30 AM
- Afternoon Walk @ 2:00 PM
- Lunch @ 1:00 PM
- Evening Medication @ 8:00 PM

### Available Cognitive Tests
1. **Memory Recall** - Short-term memory test
2. **Pattern & Logic** - Logic puzzle test
3. **Color Test** - Color identification

### Mood Options
- 😊 Very Happy
- 😄 Happy
- 😐 Neutral
- 😢 Sad
- 😞 Very Sad
- 😰 Anxious

---

## 🔐 Security Features

✅ **CSRF Protection** - All forms protected with CSRF tokens
✅ **Password Security** - Passwords hashed with PBKDF2
✅ **Session Authentication** - Secure session management
✅ **Role-Based Access Control** - Users can only access their role's features
✅ **SQL Injection Protection** - Django ORM prevents SQL injection
✅ **XSS Protection** - Django templates auto-escape variables
✅ **User Input Validation** - All forms validate input

---

## 📞 Support

**Documentation**: See `COMPLETE_APPLICATION_GUIDE.md`
**Quick Start**: See `QUICK_START.md`
**Project Structure**: See `PROJECT_STRUCTURE.md`

---

## ✨ Version Info

- **Application**: MemoryCare v1.0.0
- **Framework**: Django 4.2.7
- **Python**: 3.14.0
- **Status**: ✅ Production Ready

---

**Happy Coding! 🎉**
