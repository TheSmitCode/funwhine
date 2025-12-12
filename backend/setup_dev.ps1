# setup_dev.ps1
# Usage:  .\setup_dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== FUNWINE dev setup script ==="


### 1) Create venv
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating venv in .venv..."
    python -m venv .venv
} else {
    Write-Host "Using existing venv .venv"
}


### 2) Activate venv
$activate = Join-Path -Path (Resolve-Path ".venv").Path -ChildPath "Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
} else {
    Write-Warning "Could not find Activate.ps1 at $activate"
}


### 3) Install requirements
if (Test-Path "requirements.txt") {
    Write-Host "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
} else {
    Write-Warning "requirements.txt not found."
}


### 4) Ensure config/.env exists
$configDir = Join-Path (Get-Location) "config"
$envPath = Join-Path $configDir ".env"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

if (-not (Test-Path $envPath)) {
    New-Item -ItemType File -Path $envPath | Out-Null
}

### Helper: safely append KEY=value only if missing
function EnsureKey {
    param(
        [string]$File,
        [string]$Key,
        [string]$DefaultValue
    )

    $content = Get-Content $File -Raw
    if ($content -notmatch "(?m)^$([regex]::Escape($Key))=") {
        "$Key=$DefaultValue" | Out-File -Append -FilePath $File
        Write-Host "Added $Key"
    } else {
        Write-Host "$Key already exists"
    }
}


### SECRET_KEY
$fallbackSecret = [guid]::NewGuid().ToString()
EnsureKey -File $envPath -Key "SECRET_KEY" -DefaultValue $fallbackSecret


### BOOTSTRAP_ADMIN_PASSWORD
EnsureKey -File $envPath -Key "BOOTSTRAP_ADMIN_PASSWORD" -DefaultValue "IfAtFirst123!"


### BOOTSTRAP_ADMIN_DISPLAY_NAME
EnsureKey -File $envPath -Key "BOOTSTRAP_ADMIN_DISPLAY_NAME" -DefaultValue "Administrator"


### 5) Init DB (create tables)
Write-Host "Running init_db()..."

$pythonScript = @"
from app.db.session import init_db
init_db()
print('init_db() executed')
"@

python -c $pythonScript


### 6) Create admin user
Write-Host "Creating admin user..."
# use bootstrap_admin.py (async-aware) instead of a non-existent create_admin.py
python bootstrap_admin.py


### 7) Start Uvicorn
Write-Host "Starting uvicorn at http://127.0.0.1:8000"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
