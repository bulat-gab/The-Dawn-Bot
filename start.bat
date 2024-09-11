@echo off

if not exist venv (
    echo Calling .\scripts\install.bat to install python virtual environment...
    call .\scripts\install.bat
)

echo Starting the bot...
python run.py

