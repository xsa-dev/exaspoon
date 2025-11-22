@echo off
REM SpoonAI Automatic Setup Script with uv for Windows
REM This script automatically sets up the environment using uv

echo 🥄 Setting up SpoonAI environment with uv...

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ uv is not installed. Please install uv first:
    echo    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo    or visit https://github.com/astral-sh/uv
    exit /b 1
)

echo ✅ uv detected

REM Create virtual environment and install dependencies
echo 📦 Creating virtual environment and installing dependencies...
uv sync

REM Copy .env.example to .env if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys and configuration
)

echo.
echo 🎉 SpoonAI setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys and configuration
echo 2. Run tests: uv run pytest
echo 3. Start the application: uv run python -m spoon_ai
echo 4. Activate shell: uv shell
echo.
echo For more information, see README.md
pause
