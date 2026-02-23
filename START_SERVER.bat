@echo off
echo ========================================
echo MemoryCare - Starting Server
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set SQLite mode (if MySQL is not available)
set USE_SQLITE=True

echo [INFO] Starting Django development server...
echo [INFO] Server will be available at http://127.0.0.1:8000/
echo [INFO] Press CTRL+C to stop the server
echo.

python manage.py runserver

pause
