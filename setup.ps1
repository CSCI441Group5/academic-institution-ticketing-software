# Creates .venv if needed and installs dependencies.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt

Write-Host "Setup complete. Run the app with: .\run.ps1"
