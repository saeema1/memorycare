# 🚀 Step-by-Step Guide: How to Run MemoryCare Project

Follow these steps **exactly in order** to run the project successfully.

---

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Python 3.8+ installed
- ✅ Project folder: `C:\Users\user\OneDrive\Desktop\memorycare`
- ✅ Virtual environment created (or we'll create it)

---

## Step 1: Open PowerShell

1. Press `Windows Key + X`
2. Select **"Windows PowerShell"** or **"Terminal"**
3. Navigate to project folder:
   ```powershell
   cd "C:\Users\user\OneDrive\Desktop\memorycare"
   ```

---

## Step 2: Activate Virtual Environment

Type this command:
```powershell
.\venv\Scripts\Activate.ps1
```

**Expected result:** You should see `(venv)` at the beginning of your command prompt:
```
(venv) PS C:\Users\user\OneDrive\Desktop\memorycare>
```

**If you get an error:** The venv might not exist. Skip to Step 2b.

### Step 2b: Create Virtual Environment (if needed)

If Step 2 failed, create the venv first:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

## Step 3: Install Dependencies

Install all required packages:
```powershell
python -m pip install -r requirements.txt
```

**Expected result:** You'll see packages being downloaded and installed. Wait until it finishes.

**Time:** This may take 2-5 minutes depending on your internet speed.

---

## Step 4: Set Database Mode

We'll use SQLite (no MySQL needed):
```powershell
$env:USE_SQLITE = "True"
```

**Note:** This tells Django to use SQLite instead of MySQL, so you don't need MySQL running.

---

## Step 5: Create Database Tables

Run migrations to create the database:
```powershell
python manage.py makemigrations
```

**Expected result:**
```
Migrations for 'accounts':
  accounts\migrations\0001_initial.py
    - Create model User
```

Then apply migrations:
```powershell
python manage.py migrate
```

**Expected result:** You'll see many "OK" messages as tables are created.

---

## Step 6: Create Admin User (Doctor)

Create a doctor account:
```powershell
python manage.py create_doctor
```

**You'll be prompted to enter:**
- Username: (type any username, e.g., `admin`)
- Email: (type your email, e.g., `admin@example.com`)
- Password: (type a password, e.g., `AdminPass123!`)
- Password (again): (type the same password)

**OR use this command to skip prompts:**
```powershell
python manage.py create_doctor --username admin --email admin@example.com --password AdminPass123! --first-name Admin --last-name User
```

**Expected result:**
```
Successfully created doctor user: admin
```

---

## Step 7: Start the Server

Start the Django development server:
```powershell
python manage.py runserver
```

**Expected result:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 15, 2025 - 10:30:00
Django version 4.2.7, using settings 'memorycare.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Important:** Keep this window open! The server is now running.

---

## Step 8: Open in Browser

1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Go to: **http://127.0.0.1:8000/**

**Expected result:** You should see the MemoryCare login page.

---

## Step 9: Login

Use the credentials you created in Step 6:
- **Username:** `admin` (or what you entered)
- **Password:** `AdminPass123!` (or what you entered)

Click **"Login"**

**Expected result:** You'll see the Doctor Dashboard with statistics.

---

## ✅ Success! You're Running the Project

Now you can:
- ✅ View the Doctor Dashboard
- ✅ Create new users (Caregivers/Patients)
- ✅ View all users
- ✅ Access Admin Panel at http://127.0.0.1:8000/admin/
- ✅ Test API at http://127.0.0.1:8000/api/users/

---

## 🛑 How to Stop the Server

When you're done:
1. Go back to the PowerShell window
2. Press `CTRL + C`
3. Type `Y` and press Enter (if prompted)

---

## 🔄 Running Again Later

Next time you want to run the project, you only need:

```powershell
cd "C:\Users\user\OneDrive\Desktop\memorycare"
.\venv\Scripts\Activate.ps1
$env:USE_SQLITE = "True"
python manage.py runserver
```

(Steps 3-6 are only needed once)

---

## ⚠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'django'"
**Solution:** Make sure venv is activated (Step 2). You should see `(venv)` in your prompt.

### Problem: "Can't connect to MySQL server"
**Solution:** Make sure you ran Step 4: `$env:USE_SQLITE = "True"`

### Problem: "Port 8000 is already in use"
**Solution:** Use a different port:
```powershell
python manage.py runserver 8001
```
Then access: http://127.0.0.1:8001/

### Problem: "ERR_CONNECTION_REFUSED" in browser
**Solution:** Make sure Step 7 completed successfully and server is running.

### Problem: "AttributeError: 'function' object has no attribute 'as_view'"
**Solution:** This is already fixed. Make sure you have the latest code.

---

## 📝 Quick Command Summary

Copy-paste these commands in order:

```powershell
# 1. Navigate to project
cd "C:\Users\user\OneDrive\Desktop\memorycare"

# 2. Activate venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies (first time only)
python -m pip install -r requirements.txt

# 4. Set SQLite mode
$env:USE_SQLITE = "True"

# 5. Create migrations (first time only)
python manage.py makemigrations
python manage.py migrate

# 6. Create doctor user (first time only)
python manage.py create_doctor

# 7. Start server
python manage.py runserver
```

---

## 🎯 What Each Step Does

- **Step 1-2:** Sets up Python environment
- **Step 3:** Installs Django and other packages
- **Step 4:** Chooses SQLite database (easier than MySQL)
- **Step 5:** Creates database tables
- **Step 6:** Creates admin account to login
- **Step 7:** Starts the web server
- **Step 8-9:** Access and use the application

---

## ✅ Verification Checklist

After completing all steps, verify:
- [ ] PowerShell shows `(venv)` prefix
- [ ] Server shows "Starting development server at http://127.0.0.1:8000/"
- [ ] Browser opens login page at http://127.0.0.1:8000/
- [ ] Can login with doctor credentials
- [ ] Doctor dashboard displays correctly

---

## 🎉 You're Done!

If you can see the login page and dashboard, **Phase 1 is successfully running!**

For more details, see:
- `COMPLETE_SETUP_GUIDE.md` - Detailed guide
- `PHASE1_FINAL_STATUS.md` - Feature list

---

**Need help?** Check the troubleshooting section above or review error messages carefully.
