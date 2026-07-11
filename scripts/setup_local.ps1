# Setup local Roboflow Inference on Python 3.12 (Windows)
# Usage: .\scripts\setup_local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$py312 = "C:\Users\jbdt\AppData\Roaming\uv\python\cpython-3.12.8-windows-x86_64-none\python.exe"
if (-not (Test-Path $py312)) {
  Write-Host "Python 3.12 not found at uv path. Trying: py -3.12"
  py -3.12 -m venv .venv312
} else {
  & $py312 -m venv .venv312
}

.\.venv312\Scripts\python -m pip install --upgrade pip
.\.venv312\Scripts\pip install -r requirements-local.txt

Write-Host ""
Write-Host "Done. Activate and run:"
Write-Host "  .\.venv312\Scripts\Activate.ps1"
Write-Host "  python -m skytrace.cli status"
Write-Host "  python -m skytrace.cli track --backend local --roboflow-model airborne --source data/videos/undershot_a380_yyz.webm --max-frames 60"
