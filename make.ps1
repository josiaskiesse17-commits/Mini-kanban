param(
    [Parameter(Position = 0)]
    [ValidateSet("install", "backend", "frontend", "dev", "test", "test-backend", "build", "seed", "clean")]
    [string]$Target = "dev"
)

$Root = $PSScriptRoot
$VenvPy = Join-Path $Root "backend\.venv\Scripts\python.exe"

function Invoke-Install {
    python -m venv (Join-Path $Root "backend\.venv")
    & $VenvPy -m pip install -r (Join-Path $Root "backend\requirements.txt")
    Push-Location (Join-Path $Root "frontend")
    try { npm install } finally { Pop-Location }
}

function Invoke-Backend {
    Set-Location (Join-Path $Root "backend")
    & $VenvPy -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

function Invoke-Frontend {
    Set-Location (Join-Path $Root "frontend")
    npm run dev
}

function Invoke-Dev {
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "Set-Location '$Root'; .\make.ps1 backend"
    Start-Process powershell -ArgumentList "-NoProfile", "-Command", "Set-Location '$Root'; .\make.ps1 frontend"
}

function Invoke-Test {
    Push-Location (Join-Path $Root "backend")
    try { & $VenvPy -m pytest } finally { Pop-Location }
}

function Invoke-Build {
    Push-Location (Join-Path $Root "frontend")
    try { npm run build } finally { Pop-Location }
}

function Invoke-Seed {
    Push-Location (Join-Path $Root "backend")
    try { & $VenvPy -m app.seed } finally { Pop-Location }
}

function Invoke-Clean {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root "frontend\dist")
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root "backend\.pytest_cache")
    Get-ChildItem (Join-Path $Root "backend") -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force
}

switch ($Target) {
    "install" { Invoke-Install }
    "backend" { Invoke-Backend }
    "frontend" { Invoke-Frontend }
    "dev" { Invoke-Dev }
    "test" { Invoke-Test }
    "test-backend" { Invoke-Test }
    "build" { Invoke-Build }
    "seed" { Invoke-Seed }
    "clean" { Invoke-Clean }
}
