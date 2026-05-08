@echo off
echo.
echo  AdaptLearn -- Quick Setup (Windows)
echo  ====================================
echo.

:: Create venv
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate
call venv\Scripts\activate.bat
echo Virtual environment activated

:: Install
echo Installing dependencies...
pip install -r requirements.txt -q
echo Dependencies installed

:: .env
if not exist .env (
    copy .env.example .env
    echo .env created -- edit it to add your API keys
)

:: Migrations
echo Running migrations...
python manage.py makemigrations learning
python manage.py migrate
echo Database migrated

:: Seed
echo Seeding demo data...
python manage.py seed_data

echo.
echo ======================================
echo  Setup complete! Run:
echo.
echo    python manage.py runserver
echo.
echo  Visit: http://127.0.0.1:8000/
echo  Admin: admin / admin123
echo ======================================
pause
