param(
    [string]$OllamaUrl = "http://127.0.0.1:11434",
    [string]$VenvName = ".venv"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPath = Join-Path $ProjectRoot $VenvName
$PythonVenv = Join-Path $VenvPath "Scripts\python.exe"
$LogDir = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDir "setup_wizard_last.log"

function Write-Line { Write-Host "" }
function Write-Title($text) {
    Write-Line
    Write-Host "============================================================" -ForegroundColor DarkCyan
    Write-Host " $text" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor DarkCyan
}
function Write-Step($text) { Write-Host "[STEP] $text" -ForegroundColor Cyan }
function Write-OK($text) { Write-Host "[OK]   $text" -ForegroundColor Green }
function Write-Warn($text) { Write-Host "[WARN] $text" -ForegroundColor Yellow }
function Write-Fail($text) { Write-Host "[FAIL] $text" -ForegroundColor Red }
function Pause-Wizard { Write-Line; Read-Host "Press Enter to continue" | Out-Null }
function Write-Log($text) {
    if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $text"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}
function Ask-Choice($prompt, $default) {
    $v = Read-Host "$prompt [$default]"
    if ([string]::IsNullOrWhiteSpace($v)) { return $default }
    return $v.Trim()
}
function Test-Command($name) { return $null -ne (Get-Command $name -ErrorAction SilentlyContinue) }

function Get-PythonCommand {
    $candidates = @()
    if (Test-Command "py") { $candidates += @{Exe="py"; Args=@("-3"); Label="py -3"} }
    if (Test-Command "python") { $candidates += @{Exe="python"; Args=@(); Label="python"} }
    if (Test-Command "python3") { $candidates += @{Exe="python3"; Args=@(); Label="python3"} }

    foreach ($c in $candidates) {
        try {
            $out = & $c.Exe @($c.Args + @("-c", "import sys; print(sys.version_info[0]); print('.'.join(map(str, sys.version_info[:3])))")) 2>$null
            if ($LASTEXITCODE -eq 0 -and $out[0] -eq "3") {
                return @{Exe=$c.Exe; Args=$c.Args; Label=$c.Label; Version=$out[1]}
            }
        } catch {}
    }
    return $null
}

function Invoke-HostPython($cmd, $args) {
    & $cmd.Exe @($cmd.Args + $args)
    return $LASTEXITCODE
}

function Ensure-Folders {
    Write-Step "Preparing folders"
    foreach ($folder in @("logs", "results", "reports", "reports\figures", "reports\figures\model_radars", "defenses")) {
        $p = Join-Path $ProjectRoot $folder
        if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
    }
    Write-OK "Output folders are ready."
}

function Check-RequiredFiles {
    Write-Step "Checking required project files"
    $required = @(
        "src\run_benchmark.py",
        "semi_auto_ollama.py",
        "attacks\attacks.json",
        "requirements.txt",
        "defenses\defense_config.json"
    )
    foreach ($r in $required) {
        $p = Join-Path $ProjectRoot $r
        if (-not (Test-Path $p)) { throw "Missing required file: $r" }
    }
    Write-OK "Project files look complete."
}

function Ensure-Venv {
    Write-Title "Step 1 - Python and Virtual Environment"
    $py = Get-PythonCommand
    if (-not $py) {
        Write-Fail "Python 3 was not found in PATH."
        Write-Host "Install Python 3.9+ first, then run this wizard again."
        throw "Python 3 not found"
    }
    Write-OK "Python found: $($py.Label), version $($py.Version)"

    if ((Test-Path $VenvPath) -and (-not (Test-Path $PythonVenv))) {
        Write-Warn "Broken virtual environment detected. Removing .venv."
        Remove-Item -Recurse -Force $VenvPath
    }
    if (-not (Test-Path $PythonVenv)) {
        Write-Step "Creating virtual environment: $VenvName"
        Invoke-HostPython $py @("-m", "venv", $VenvPath) | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }
    }
    Write-OK "Virtual environment ready: $PythonVenv"
}

function Install-Dependencies {
    Write-Title "Step 2 - Install Python Dependencies"
    if (-not (Test-Path $PythonVenv)) { throw "Virtual environment is missing." }
    Write-Step "Upgrading pip"
    & $PythonVenv -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

    Write-Step "Installing requirements.txt"
    & $PythonVenv -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }
    Write-OK "Dependencies installed."
}

function Test-OllamaApi {
    try {
        Invoke-WebRequest -Uri ($OllamaUrl.TrimEnd('/') + "/api/tags") -UseBasicParsing -TimeoutSec 4 | Out-Null
        return $true
    } catch { return $false }
}

function Check-Ollama {
    Write-Title "Step 3 - Ollama Check"
    if (-not (Test-Command "ollama")) {
        Write-Warn "Ollama command not found."
        Write-Host "Install Ollama manually from the official installer, or use winget if available."
        $install = Ask-Choice "Try winget install Ollama now? y/n" "n"
        if ($install.ToLower() -eq "y") {
            if (-not (Test-Command "winget")) { throw "winget is not available. Please install Ollama manually." }
            winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements
        }
    }
    if (-not (Test-Command "ollama")) { throw "Ollama is still not available." }
    Write-OK "Ollama command found."
    try { ollama --version } catch {}

    if (Test-OllamaApi) {
        Write-OK "Ollama API reachable: $OllamaUrl"
        return
    }

    Write-Warn "Ollama API is not reachable."
    $start = Ask-Choice "Start 'ollama serve' in a new minimized PowerShell window? y/n" "y"
    if ($start.ToLower() -eq "y") {
        Start-Process powershell -WindowStyle Minimized -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command ollama serve"
        Start-Sleep -Seconds 5
    }
    if (Test-OllamaApi) {
        Write-OK "Ollama API is reachable now."
    } else {
        Write-Warn "Ollama API is still not reachable. You can still use mock quick test, but Ollama model tests will fail."
    }
}

function Show-Models {
    Write-Title "Installed Ollama Models"
    if (Test-Command "ollama") {
        try { ollama list } catch { Write-Warn "Could not list Ollama models." }
    } else {
        Write-Warn "Ollama command not available."
    }
}

function Run-InteractiveTool {
    Write-Title "Launch Interactive Benchmark Menu"
    if (-not (Test-Path $PythonVenv)) { throw "Virtual environment is missing." }
    & $PythonVenv (Join-Path $ProjectRoot "semi_auto_ollama.py")
}

function Run-MockQuickTest {
    Write-Title "Mock Quick Test"
    & $PythonVenv (Join-Path $ProjectRoot "src\run_benchmark.py") --model mock --quick-test --defense skill_defense --no-report
    if ($LASTEXITCODE -eq 0) { Write-OK "Mock quick test passed." } else { Write-Fail "Mock quick test failed." }
}

function Run-OllamaQuickTest {
    Write-Title "Ollama Quick Test"
    Show-Models
    $model = Ask-Choice "Enter Ollama model name, for example gemma3:12b" "gemma3:12b"
    $defense = Ask-Choice "Defense mode: none / prompt_defense / skill_defense" "skill_defense"
    & $PythonVenv (Join-Path $ProjectRoot "src\run_benchmark.py") --model "ollama:$model" --quick-test --defense $defense --confirm
    if ($LASTEXITCODE -eq 0) { Write-OK "Ollama quick test completed." } else { Write-Fail "Ollama quick test failed." }
}

function Run-PlanOnly {
    Write-Title "Plan-only Test Preview"
    $ids = Ask-Choice "Attack IDs: all or A01,A02" "A01,A02"
    $styles = Ask-Choice "Styles: all / en_pure / zh_pure" "en_pure"
    $runs = Ask-Choice "Runs" "1"
    $defense = Ask-Choice "Defense mode" "none"
    & $PythonVenv (Join-Path $ProjectRoot "src\run_benchmark.py") --model mock --attack-ids $ids --styles $styles --runs $runs --defense $defense --plan-only
}

function Full-Setup {
    Write-Title "LLM Secret Guard Setup Wizard"
    Write-Host "This wizard will prepare the local experiment tool step by step."
    Write-Host "It does not change your scoring or invalid-sample rules."
    Write-Host "Project root: $ProjectRoot"
    Write-Log "Wizard started. ProjectRoot=$ProjectRoot"
    Ensure-Folders
    Check-RequiredFiles
    Ensure-Venv
    Install-Dependencies
    Check-Ollama
    Write-OK "Setup finished."
}

function Main-Menu {
    while ($true) {
        Write-Title "LLM Secret Guard - Installer Wizard"
        Write-Host "1. Full setup: check files, create venv, install dependencies, check Ollama"
        Write-Host "2. Full setup and launch interactive benchmark menu"
        Write-Host "3. Mock quick test only"
        Write-Host "4. Ollama quick test only"
        Write-Host "5. Plan-only preview, no model call"
        Write-Host "6. Launch interactive benchmark menu"
        Write-Host "7. Show installed Ollama models"
        Write-Host "0. Exit"
        Write-Line
        $choice = Read-Host "Choose an option"
        try {
            switch ($choice) {
                "1" { Full-Setup; Pause-Wizard }
                "2" { Full-Setup; Run-InteractiveTool; Pause-Wizard }
                "3" { Ensure-Folders; Check-RequiredFiles; Ensure-Venv; Install-Dependencies; Run-MockQuickTest; Pause-Wizard }
                "4" { Ensure-Folders; Check-RequiredFiles; Ensure-Venv; Install-Dependencies; Check-Ollama; Run-OllamaQuickTest; Pause-Wizard }
                "5" { Ensure-Folders; Check-RequiredFiles; Ensure-Venv; Install-Dependencies; Run-PlanOnly; Pause-Wizard }
                "6" { Ensure-Folders; Check-RequiredFiles; Ensure-Venv; Run-InteractiveTool; Pause-Wizard }
                "7" { Show-Models; Pause-Wizard }
                "0" { Write-OK "Bye."; return }
                default { Write-Warn "Unknown option."; Pause-Wizard }
            }
        } catch {
            Write-Fail $_.Exception.Message
            Write-Log "ERROR: $($_.Exception.Message)"
            Pause-Wizard
        }
    }
}

Set-Location $ProjectRoot
Main-Menu
