@echo off

REM Check for administrator privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on your system.
    echo Please install Python and try again.
    echo Press any key to exit...
    pause >nul
    exit /b
)

REM Installing virtualenv
pip install virtualenv

REM Change to the directory where the script is located
cd /d "%~dp0"

REM Check if the virtual environment ".venv" exists
echo Checking if the virtual environment ".venv" exists...
if not exist ".venv" (
    echo Virtual environment not found. Creating virtual environment in "%~dp0.venv"...
    @REM python -m venv .venv
    virtualenv -p python3.12 .venv
    if %errorlevel% neq 0 (
        echo Failed to create the virtual environment. Exiting...
        exit /b
    )
    echo Virtual environment created successfully.
)

REM Activate the virtual environment
echo Activating the virtual environment...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate the virtual environment. Exiting...
    exit /b
)

REM Construct full path to pip dynamically
set "MAIN_PY_PATH=%~dp0venv\Scripts\pip"

REM Installing dependencies
echo Installing dependencies...
pip install -U setuptools wheel
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Exiting...
    exit /b
)
echo Environment setup complete.
echo.

REM Construct full path to main.py dynamically
set "MAIN_PY_PATH=%~dp0main.py"

REM Run main.py
if exist "%MAIN_PY_PATH%" (
    echo Running main.py...
    echo.
    python "%MAIN_PY_PATH%"
    if %errorlevel% neq 0 (
        echo main.py execution failed. Exiting...
        exit /b
    )
) else (
    echo main.py not found in the current directory. Exiting...
    exit /b
)
