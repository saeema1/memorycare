# MemoryCare - Quick Start Guide

## 🚀 Fast Setup (5 Minutes)

### Step 1: Open PowerShell
```powershell
cd "C:\Users\user\OneDrive\Desktop\memorycare"
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```
You should see `(venv)` in your prompt.

### Step 3: Install Dependencies (First Time Only)
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Set SQLite Mode (No MySQL Needed)
```powershell
$env:USE_SQLITE = "True"
```

### Step 5: Create Database Tables (First Time Only)
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Doctor User (First Time Only)
```powershell
python manage.py create_doctor
```
Or use:
```powershell
python manage.py create_doctor --username admin --email admin@example.com --password AdminPass123! --first-name Admin --last-name User
```

### Step 7: Start Server
```powershell
python manage.py runserver
```

### Step 8: Access Application
Open browser and go to:
- **Login**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **API**: http://127.0.0.1:8000/api/users/

**Login Credentials:**
- Username: `admin`
- Password: `AdminPass123!`

## 📋 Important Notes

1. **After creating superuser**: Go to admin panel → Users → Select your user → Set Role to "Doctor (Admin)" → Save

2. **Alternative**: Use management command:
   ```bash
   python manage.py create_doctor
   ```

3. **MySQL Issues?**: Use pymysql instead:
   ```bash
   pip install pymysql
   ```
   Then add to `memorycare/__init__.py`:
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

## 🎯 Test the System

1. **Login** as Doctor
2. **Create Caregiver**: Dashboard → Create User → Select "Caregiver"
3. **Create Patient**: Dashboard → Create User → Select "Patient"
4. **View Users**: Dashboard → All Users
5. **Test API**: Login → Visit `/api/users/me/`

## 📚 Documentation

- **Full Setup**: See `SETUP.md`
- **Project Details**: See `README.md`
- **Structure**: See `PROJECT_STRUCTURE.md`
- **Summary**: See `PHASE1_SUMMARY.md`
