@echo off

:: If we are in the .\scripts directory then go back to the root of the project
for %%i in ("%cd%") do set CURRENT_DIR=%%~nxi
:: Check if the current directory is 'scripts'
if "%CURRENT_DIR%" == "scripts" (
    echo Currently in 'scripts' folder. Moving to parent directory...
    cd ..
)


if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist venv\Lib\site-packages\installed (
    if exist requirements.txt (
		echo installing wheel for faster installing
		pip install wheel
        echo Installing dependencies...
        pip install -r requirements.txt
        echo. > venv\Lib\site-packages\installed
    ) else (
        echo requirements.txt not found, skipping dependency installation.
    )
) else (
    echo Dependencies already installed, skipping installation.
)