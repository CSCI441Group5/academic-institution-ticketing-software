# Runs the Flask app using the local virtual environment.
# Requires .venv to be created first.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path ".venv")) {
    Write-Host "Missing .venv. Create it first: python -m venv .venv"
    exit 1
}

$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
& $VenvPython run.py
