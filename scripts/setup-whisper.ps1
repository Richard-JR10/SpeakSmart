$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "Backend"
$cacheDir = Join-Path $backendRoot ".cache\openai-whisper"

$backendEnvPath = Join-Path $backendRoot ".env"
$envLines = @()
if (Test-Path $backendEnvPath) {
    $envLines = Get-Content $backendEnvPath
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required to install the backend dependencies and official Whisper locally."
}

$updates = @{
    "ASR_PROVIDER" = "openai_whisper"
    "OPENAI_WHISPER_MODEL" = "small"
    "OPENAI_WHISPER_DEVICE" = "auto"
    "OPENAI_WHISPER_LANGUAGE" = "ja"
    "OPENAI_WHISPER_CACHE_DIR" = ".cache/openai-whisper"
}

foreach ($key in $updates.Keys) {
    $value = $updates[$key]
    if ($envLines | Where-Object { $_.StartsWith("$key=") }) {
        $envLines = $envLines | ForEach-Object {
            if ($_.StartsWith("$key=")) { "$key=$value" } else { $_ }
        }
    } else {
        $envLines += "$key=$value"
    }
}

Set-Content -Path $backendEnvPath -Value $envLines

New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null

Push-Location $backendRoot
try {
    uv sync
    uv run python .\scripts\prefetch_whisper_model.py
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Official OpenAI Whisper is ready for local development."
Write-Host "Provider: openai_whisper"
Write-Host "Model:    small"
Write-Host "Device:   auto"
Write-Host "Cache:    $cacheDir"
Write-Host ""
Write-Host "Restart your backend after this setup finishes."
