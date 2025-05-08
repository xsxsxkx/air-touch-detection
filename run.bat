@echo off
setlocal

REM Change to the env directory
cd env

REM Find the directory starting with "pyenv"
for /d %%d in (pyenv*) do (
    set PYENV_DIR=%%d
    goto :found
)

:found
cd ..

REM Check if a pyenv directory was found
if not defined PYENV_DIR (
    echo No pyenv directory found in env.
    pause
    exit /b 1
)

REM Activate the virtual environment
call env\%PYENV_DIR%\Scripts\activate.bat

REM Start main.py in a new terminal
start cmd /k "python src\main.py"

REM Wait for a moment to ensure main.py is running
timeout /t 2

REM Start gui.py in a new terminal
start cmd /k "python src\gui.py"

REM Deactivate the virtual environment in the original terminal
call env\%PYENV_DIR%\Scripts\deactivate.bat

endlocal