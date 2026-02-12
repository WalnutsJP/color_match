@echo off

:: Python Path
set python_path=".\venv\Scripts\python.exe"

:: Setup Python virtual environment
if not exist venv\  (
    python -m venv venv
    %python_path% -m pip install .
)

:: Running Python script
echo python -m color_match "%1" "%2" -o ".\output.png" --method mvgd --mode rgb
%python_path% -m color_match "%1" "%2" -o ".\output.png" --method mvgd --mode rgb

if %ERRORLEVEL% NEQ 0 pause
