@echo off
setlocal

REM === Settings ===
set VENV_DIR=.venv
set REQUIREMENTS=requirements.txt

REM === Check for Python ===
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found! Please add Python to your PATH.
    pause
    exit /b
)

REM === Check for venv ===
if not exist "%VENV_DIR%\" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

REM === Install dependencies ===
if exist "%REQUIREMENTS%" (
    echo [INFO] Installing dependencies from %REQUIREMENTS%...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%"
) else (
    echo [WARNING] File %REQUIREMENTS% not found. Skipping dependencies installation.
)

endlocal
pause