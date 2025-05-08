@echo off
setlocal

set curdir=%~dp0
chdir %curdir%

rem Set the starting Python version to 3.9
set START_MINOR_VER=9

rem List installed Python versions and try to find a suitable one
set FOUND=0
for /f "tokens=2 delims=." %%a in ('py -0p') do (
    for /f "tokens=1 delims=-" %%b in ("%%a") do (
        if %%b geq %START_MINOR_VER% (
            call :create_venv %%b
            if %ERRORLEVEL%==0 (
                set FOUND=1
                set PYTHON_VER=3.%%b
                set NAME=pyenv3%%b
                goto :after_loop
            )
        )
    )
)

if %FOUND%==0 (
    echo Failed to find a suitable Python version to create a virtual environment
    pause
    exit /b 1
)

:after_loop

call :check_venv
call :error_check
call :pip_upgrade
call :error_check
call :pip_install
call :error_check

goto :end

:create_venv
    set PY_VER=%1
    echo Attempting to create virtual environment with Python 3.%PY_VER%
    py -3.%PY_VER% -m venv pyenv3%PY_VER%
    if %ERRORLEVEL% neq 0 (
        echo Failed to create virtual environment with Python 3.%PY_VER%
        pause
    )
    exit /b %ERRORLEVEL%

:check_venv
    echo Checking virtual environment
    %NAME%\Scripts\python --version | find /i "%PYTHON_VER%"
    if %ERRORLEVEL% neq 0 (
        echo Failed to verify virtual environment with Python %PYTHON_VER%
        pause
    )
    exit /b %ERRORLEVEL%

:pip_upgrade
    echo Upgrading pip
    %NAME%\Scripts\python -m pip install pip==25.0.1 --proxy=http://proxy.mei.co.jp:8080
    %NAME%\Scripts\pip --version | find /i "25.0.1"
    if %ERRORLEVEL% neq 0 (
        echo Failed to upgrade pip
        pause
    )
    exit /b %ERRORLEVEL%

:pip_install
    echo Installing packages
    %NAME%\Scripts\pip install -r requirements.txt --proxy=http://proxy.mei.co.jp:8080
    if %ERRORLEVEL% neq 0 (
        echo Failed to install packages
        pause
    )
    exit /b %ERRORLEVEL%

:error_check
    if %ERRORLEVEL% neq 0 (
        rmdir /s /q %NAME%
        echo;
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    exit /b 0

:end
endlocal
echo Successfully created virtual environment
pause
exit /b 0