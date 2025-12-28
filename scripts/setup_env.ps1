# Usage: Open PowerShell in project root and run: .\scripts\setup_env.ps1
# Creates a .venv, activates it, upgrades pip, installs requirements, and initializes DB

Write-Output "Creating virtual environment .venv..."
python -m venv .venv

if (-Not (Test-Path -Path ".venv\Scripts\Activate.ps1")) {
  Write-Error "Failed to create virtual environment. Please ensure Python is installed and writable to this folder."
  exit 1
}

Write-Output "Activating virtual environment..."
. .venv\Scripts\Activate.ps1

Write-Output "Upgrading pip..."
python -m pip install --upgrade pip

Write-Output "Installing requirements from requirements.txt..."
python -m pip install -r requirements.txt

Write-Output "Installing Playwright browsers (for E2E tests)..."
# Playwright Python requires installing browser binaries separately
python -m playwright install

Write-Output "Initializing database (sqlite dev.db by default)..."
# Set a sqlite local DB if no SQLALCHEMY_DATABASE_URI provided
if (-Not $env:SQLALCHEMY_DATABASE_URI) {
  $env:SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
}
python scripts/init_db.py

Write-Output "Setup complete. Start server: python -m src.server and open http://localhost:5000"
