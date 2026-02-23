@echo off
echo ========================================
echo MemoryCare Project Setup and Run Script
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [INFO] Creating .env file template...
    (
        echo SECRET_KEY=django-insecure-change-this-to-a-random-secret-key-in-production
        echo DEBUG=True
        echo DB_NAME=memorycare_db
        echo DB_USER=root
        echo DB_PASSWORD=
        echo DB_HOST=localhost
        echo DB_PORT=3306
    ) > .env
    echo [INFO] .env file created. Please edit it with your MySQL credentials.
    echo.
    pause
)

REM Check if venv exists
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [INFO] Virtual environment created.
    echo.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure MySQL is running
echo 2. Create database: CREATE DATABASE memorycare_db;
echo 3. Edit .env file with your MySQL password
echo 4. Run: python manage.py makemigrations
echo 5. Run: python manage.py migrate
echo 6. Run: python manage.py create_doctor
echo 7. Run: python manage.py runserver
echo.
echo Press any key to continue to migrations...
pause

REM Run migrations
echo.
echo [INFO] Creating migrations...
python manage.py makemigrations

echo.
echo [INFO] Applying migrations...
python manage.py migrate

echo.
echo ========================================
echo Would you like to:
echo 1. Create a doctor user
echo 2. Run the server
echo 3. Exit
echo ========================================
choice /c 123 /n /m "Enter your choice: "

if errorlevel 3 goto end
if errorlevel 2 goto runserver
if errorlevel 1 goto createdoctor

:createdoctor
echo.
python manage.py create_doctor
echo.
goto runserver

:runserver
echo.
echo [INFO] Starting development server...
echo [INFO] Server will be available at http://127.0.0.1:8000/
echo [INFO] Press CTRL+C to stop the server
echo.
python manage.py runserver
goto end

:end
echo.
echo Thank you for using MemoryCare!
pause
