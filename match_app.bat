@echo off

:: Python Path
set python_path=".\venv\Scripts\python.exe"

:: Setup Python virtual environment
if not exist venv\  (
    python -m venv venv
    %python_path% -m pip install .
)

:: Check tkinterdnd2
%python_path% -m pip show tkinterdnd2 >nul 2>&1
if errorlevel 1 (
    %python_path% -m pip install tkinterdnd2
)

:: Running Python script
%python_path% source\color_match_app.py

if %ERRORLEVEL% NEQ 0 pause
