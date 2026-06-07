# download_modis_phase1.ps1
# Phase-1 MODIS download for Nature climate/ecology project.
# Downloads MOD13Q1.061 + MYD13Q1.061 for target Australian FLUXNET tiles only.
# Stops before/when local output size reaches MaxGB.

param(
    [string]$OutputRoot = "W:\Nature\data\raw\modis",
    [int]$StartYear = 2001,
    [int]$EndYear = 2025,
    [double]$MaxGB = 100
)

$ErrorActionPreference = "Stop"

$Token = $env:EDL_TOKEN
if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "EDL_TOKEN environment variable is empty. In this PowerShell window, run: `$env:EDL_TOKEN='your_token_here'"
}

$BaseUrl = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61"
$Products = @("MOD13Q1", "MYD13Q1")
$Tiles = @("h31v11", "h29v12", "h32v10", "h32v12")
$MaxBytes = [int64]($MaxGB * 1GB)

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

function Get-DownloadedBytes {
    param([string]$Root)
    if (-not (Test-Path $Root)) { return [int64]0 }
    $sum = (Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $sum) { return [int64]0 }
    return [int64]$sum
}

function Format-Bytes {
    param([int64]$Bytes)
    return "{0:N2} GB" -f ($Bytes / 1GB)
}

function Get-RemoteFileNames {
    param(
        [string]$DirectoryUrl,
        [string]$Product,
        [string]$DatePrefix,
        [string[]]$TargetTiles
    )

    try {
        $response = Invoke-WebRequest `
            -Uri $DirectoryUrl `
            -Headers @{ Authorization = "Bearer $Token" } `
            -UseBasicParsing `
            -MaximumRedirection 5 `
            -ErrorAction Stop
    }
    catch {
        Write-Host "SKIP directory not available: $DirectoryUrl"
        return @()
    }

    $html = $response.Content
    $found = New-Object System.Collections.Generic.List[string]

    foreach ($tile in $TargetTiles) {
        $pattern = "$Product\.$DatePrefix\.$tile\.061\.[^`"'<>\s]+\.hdf"
        foreach ($match in [regex]::Matches($html, $pattern)) {
            if (-not $found.Contains($match.Value)) {
                $found.Add($match.Value)
            }
        }
    }

    return $found.ToArray()
}

function Download-OneFile {
    param(
        [string]$Url,
        [string]$Destination
    )

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    if ((Test-Path $Destination) -and ((Get-Item $Destination).Length -gt 0)) {
        Write-Host "EXISTS $Destination"
        return
    }

    $tmp = "$Destination.partial"
    Write-Host "DOWNLOADING $Url"
    Write-Host "        -> $Destination"

    # curl.exe is bundled with current Windows versions and supports resume (-C -).
    & curl.exe `
        -L `
        -b session `
        -C - `
        --fail `
        --retry 5 `
        --retry-delay 10 `
        --connect-timeout 60 `
        -H "Authorization: Bearer $Token" `
        -o "$tmp" `
        "$Url"

    if ($LASTEXITCODE -ne 0) {
        throw "curl.exe failed with exit code $LASTEXITCODE for $Url"
    }

    Move-Item -Force "$tmp" "$Destination"
}

$startBytes = Get-DownloadedBytes -Root $OutputRoot
Write-Host "OutputRoot: $OutputRoot"
Write-Host "Initial downloaded size: $(Format-Bytes $startBytes)"
Write-Host "Stop threshold: $MaxGB GB"
Write-Host "Products: $($Products -join ', ')"
Write-Host "Tiles: $($Tiles -join ', ')"
Write-Host "Years: $StartYear-$EndYear"

for ($year = $StartYear; $year -le $EndYear; $year++) {
    for ($doy = 1; $doy -le 366; $doy += 16) {
        $doy3 = "{0:D3}" -f $doy
        $datePrefix = "A$year$doy3"

        foreach ($product in $Products) {
            $currentBytes = Get-DownloadedBytes -Root $OutputRoot
            if ($currentBytes -ge $MaxBytes) {
                Write-Host "STOP: downloaded size reached $(Format-Bytes $currentBytes), threshold is $MaxGB GB."
                exit 0
            }

            $dirUrl = "$BaseUrl/$product/$year/$doy3/"
            Write-Host ""
            Write-Host "CHECK $dirUrl"

            $files = Get-RemoteFileNames `
                -DirectoryUrl $dirUrl `
                -Product $product `
                -DatePrefix $datePrefix `
                -TargetTiles $Tiles

            if ($files.Count -eq 0) {
                Write-Host "No target tile files found."
                continue
            }

            foreach ($file in $files) {
                $currentBytes = Get-DownloadedBytes -Root $OutputRoot
                if ($currentBytes -ge $MaxBytes) {
                    Write-Host "STOP: downloaded size reached $(Format-Bytes $currentBytes), threshold is $MaxGB GB."
                    exit 0
                }

                $url = "$dirUrl$file"
                $dest = Join-Path $OutputRoot (Join-Path $product (Join-Path $year (Join-Path $doy3 $file)))
                Download-OneFile -Url $url -Destination $dest

                $afterBytes = Get-DownloadedBytes -Root $OutputRoot
                Write-Host "Downloaded size now: $(Format-Bytes $afterBytes)"
                if ($afterBytes -ge $MaxBytes) {
                    Write-Host "STOP: downloaded size reached $(Format-Bytes $afterBytes), threshold is $MaxGB GB."
                    exit 0
                }
            }
        }
    }
}

$finalBytes = Get-DownloadedBytes -Root $OutputRoot
Write-Host ""
Write-Host "DONE. Final downloaded size: $(Format-Bytes $finalBytes)"
