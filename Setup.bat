
@echo off
setlocal

echo ==========================================
echo       Python Environment Setup
echo ==========================================

REM Step 1: Create virtual environment
echo.
echo [1/7] Creating virtual environment...

if not exist ".venv\Scripts\python.exe" (
    uv venv
    if errorlevel 1 goto :error
) else (
    echo Virtual environment already exists. Skipping.
)

REM Step 2: Upgrade pip
echo.
echo [2/7] Upgrading pip...

.venv\Scripts\python.exe -m ensurepip --upgrade
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto :error

REM Step 3: Install dependencies
echo.
echo [3/7] Installing dependencies...

.venv\Scripts\python.exe -m pip install --only-binary=:all: PyYAML
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install python-dotenv
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install pydantic
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install google-genai
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install requests
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install streamlit
if errorlevel 1 goto :error

.venv\Scripts\python.exe -m pip install "fastapi[standard]"
if errorlevel 1 goto :error

REM Step 4: Install requirements.txt if available
echo.
echo [4/7] Installing requirements.txt...

if exist "requirements.txt" (
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 goto :error
) else (
    echo requirements.txt not found. Skipping.
)

REM Step 5: Generate requirements.txt
echo.
echo [5/7] Generating requirements.txt...

.venv\Scripts\python.exe -m pip freeze > requirements.txt
if errorlevel 1 goto :error

REM Step 6: Display installed packages
echo.
echo [6/7] Installed packages:

.venv\Scripts\python.exe -m pip list

REM Step 7: Complete
echo.
echo ==========================================
echo Environment setup completed successfully!
echo ==========================================

echo.
echo To activate your environment, run:
echo .venv\Scripts\activate.bat

goto :end

:error
echo.
echo ==========================================
echo ERROR: Environment setup failed!
echo Please check the error messages above.
echo ==========================================
exit /b 1

:end
endlocal
exit /b 0
