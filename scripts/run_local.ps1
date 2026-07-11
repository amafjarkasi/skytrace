# Run SkyTrace with local Inference (Python 3.12)
# Usage:
#   .\scripts\run_local.ps1
#   .\scripts\run_local.ps1 -Source data\videos\undershot_a380_yyz.webm -MaxFrames 120 -Model airborne
#   .\scripts\run_local.ps1 -Source data\videos\drone_quadcopter_hover.webm -Model drone -MaxFrames 0 -Zones

param(
  [string]$Source = "data\videos\undershot_a380_yyz.webm",
  [string]$Model = "airborne",
  [string]$Backend = "local",
  [int]$MaxFrames = 120,
  [double]$Conf = 0.25,
  [switch]$Zones
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$py = Join-Path $Root ".venv312\Scripts\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "Missing .venv312 — run .\scripts\setup_local.ps1 first"
  exit 1
}

& $py -m skytrace.cli status
$zoneArgs = @()
if ($Zones) { $zoneArgs = @("--zones") }

& $py -m skytrace.cli track `
  --backend $Backend `
  --roboflow-model $Model `
  --source $Source `
  --max-frames $MaxFrames `
  --conf $Conf `
  @zoneArgs
