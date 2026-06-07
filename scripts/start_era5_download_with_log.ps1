param(
    [int]$YearStart = 2000,
    [int]$YearEnd = 2000,
    [string]$Months = "1",
    [string]$LogDir = "logs"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Python virtual environment not found at $Python"
}

$env:CDSAPI_URL = [Environment]::GetEnvironmentVariable("CDSAPI_URL", "User")
$env:CDSAPI_KEY = [Environment]::GetEnvironmentVariable("CDSAPI_KEY", "User")
if (-not $env:CDSAPI_URL -or -not $env:CDSAPI_KEY) {
    throw "CDSAPI_URL/CDSAPI_KEY user environment variables are not configured."
}

$ResolvedLogDir = Join-Path $Root $LogDir
New-Item -ItemType Directory -Force -Path $ResolvedLogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutLog = Join-Path $ResolvedLogDir "era5_download_${YearStart}_${YearEnd}_m${Months}_${Stamp}.out.log"
$ErrLog = Join-Path $ResolvedLogDir "era5_download_${YearStart}_${YearEnd}_m${Months}_${Stamp}.err.log"

$Arguments = @(
    "-m", "nature_climate_ai.cli", "download-era5",
    "--year-start", "$YearStart",
    "--year-end", "$YearEnd",
    "--months", "$Months"
)

$Process = Start-Process -FilePath $Python `
    -ArgumentList $Arguments `
    -WorkingDirectory $Root `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -WindowStyle Hidden `
    -PassThru

Write-Output "Started ERA5 download process: $($Process.Id)"
Write-Output "stdout log: $OutLog"
Write-Output "stderr log: $ErrLog"
Write-Output "Watch with:"
Write-Output "  Get-Content -Path `"$OutLog`" -Wait"
