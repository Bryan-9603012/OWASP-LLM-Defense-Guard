param(
    [string]$VenvName = ".venv",
    [string]$OllamaUrl = "http://127.0.0.1:11434",
    [switch]$SkipOllamaCheck
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot $VenvName
$PythonVenv = Join-Path $VenvPath "Scripts\python.exe"
$SemiAutoScript = Join-Path $ProjectRoot "semi_auto_ollama.py"

function Write-OK { Write-Host "[OK]    $args" -ForegroundColor Green }
function Write-FAIL { Write-Host "[FAIL]  $args" -ForegroundColor Red }
function Write-INFO { Write-Host "[INFO]  $args" -ForegroundColor Cyan }
function Write-WARN { Write-Host "[WARN]  $args" -ForegroundColor Yellow }
function Write-Header { Write-Host "`n========================================`n$args`n========================================`n" -ForegroundColor Yellow }

function Test-OllamaApi {
    param([string]$Url)
    $tagsUrl = $Url.TrimEnd('/') + "/api/tags"
    try {
        $response = Invoke-WebRequest -Uri $tagsUrl -UseBasicParsing -ErrorAction Stop
        return $response.StatusCode -eq 200
    }
    catch {
        Write-WARN "Cannot reach Ollama API: $tagsUrl"
        Write-WARN "Reason: $($_.Exception.Message)"
        return $false
    }
}

Write-Header "LLM Secret Guard Semi-Auto Test"
Write-INFO "Project root: $ProjectRoot"
Write-INFO "Ollama URL: $OllamaUrl"

Set-Location $ProjectRoot

if (-not (Test-Path $PythonVenv)) {
    Write-FAIL "Virtual environment not found: $PythonVenv"
    Write-WARN "Please run installer first: .\install_and_run.ps1 -NoRun"
    exit 1
}

if (-not (Test-Path $SemiAutoScript)) {
    Write-FAIL "semi_auto_ollama.py not found"
    exit 1
}

if (-not $SkipOllamaCheck) {
    if (-not (Test-OllamaApi -Url $OllamaUrl)) {
        Write-FAIL "Ollama is not reachable."
        Write-Host "Start another terminal and run:" -ForegroundColor Yellow
        Write-Host "  ollama serve" -ForegroundColor White
        Write-Host "Then run again:" -ForegroundColor Yellow
        Write-Host "  .\test_ollama.ps1" -ForegroundColor White
        exit 1
    }
    Write-OK "Ollama API reachable"
}

$env:OLLAMA_URL = $OllamaUrl
& $PythonVenv $SemiAutoScript
exit $LASTEXITCODE
