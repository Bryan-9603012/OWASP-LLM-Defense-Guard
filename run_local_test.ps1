param(
    [string]$DistroName = "Ubuntu",
    [int]$TimeoutSec = 60,
    [switch]$EnvOnly,
    [switch]$SkipBenchmark,
    [switch]$SkipReport,
    [switch]$KeepOllama
)

$ErrorActionPreference = "Stop"
$BaseUrl = "http://localhost:11434"
$Root = $PSScriptRoot
Set-Location $Root

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor DarkGray
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor DarkGray
}

function Write-Ok {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Confirm-Yes {
    param([string]$Message)

    $answer = Read-Host "$Message (Y/n)"
    return ($answer -eq "" -or $answer.ToLower() -eq "y" -or $answer.ToLower() -eq "yes")
}

function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-WslDistros {
    $raw = & wsl.exe -l -q 2>$null

    return @(
        $raw |
        ForEach-Object { ($_ -replace "`0", "").Trim() } |
        Where-Object { $_ -ne "" }
    )
}

function Invoke-WslBash {
    param(
        [string]$Distro,
        [string]$Command
    )

    & wsl.exe -d $Distro -e bash -lc $Command
}

function Test-OllamaApi {
    try {
        Invoke-RestMethod -Uri "$BaseUrl/api/tags" -TimeoutSec 3 | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-ModelName {
    param([string]$ModelName)

    if ([string]::IsNullOrWhiteSpace($ModelName)) {
        return $false
    }

    return ($ModelName -match '^[A-Za-z0-9._/-]+(:[A-Za-z0-9._-]+)?$')
}

function Ensure-PythonDependencies {
    Write-Step "Step 1: Check Python and install dependencies"

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Fail "Python command not found."
        exit 1
    }

    python --version
    python -m pip --version

    if (-not (Test-Path "requirements.txt")) {
        Write-Fail "requirements.txt not found. Please run this script in llm-secret-guard."
        exit 1
    }

    $reqText = Get-Content "requirements.txt" -Raw
    $nonEmptyLines = @($reqText -split "`r?`n" | Where-Object { $_.Trim() -ne "" })

    if ($reqText -match "python-dotenv.*requests" -and $nonEmptyLines.Count -eq 1) {
        Write-Warn "requirements.txt looks invalid. Rewriting it."
        Set-Content -Path "requirements.txt" -Value "python-dotenv>=1.0.1`nrequests>=2.31.0" -Encoding UTF8
    }

    python -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to install Python dependencies."
        exit 1
    }

    Write-Ok "Python dependencies are ready."
}

function Ensure-WslAndUbuntu {
    Write-Step "Step 2: Check WSL and Ubuntu"

    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        Write-Fail "wsl.exe not found."

        if (Confirm-Yes "Install WSL and Ubuntu now?") {
            if (-not (Test-Admin)) {
                Write-Fail "Installing WSL requires Administrator PowerShell."
                Write-Host "Open PowerShell as Administrator and run this script again."
                exit 1
            }

            wsl --install -d $DistroName
            Write-Warn "A reboot may be required. After reboot, open Ubuntu once to finish setup."
            exit 0
        }

        exit 1
    }

    Write-Ok "wsl.exe found."

    $distros = Get-WslDistros
    $selectedDistro = $null

    if ($distros -contains $DistroName) {
        $selectedDistro = $DistroName
    }
    else {
        $selectedDistro = $distros | Where-Object { $_ -like "Ubuntu*" } | Select-Object -First 1
    }

    if (-not $selectedDistro) {
        Write-Warn "Ubuntu distro not found."

        if (Confirm-Yes "Install Ubuntu now?") {
            wsl --install -d $DistroName
            Write-Warn "After installation, open Ubuntu once to finish username and password setup."
            exit 0
        }

        exit 1
    }

    $selectedDistro = [string]$selectedDistro
    Write-Ok "Using WSL distro: $selectedDistro"

    $ubuntuInfo = & wsl.exe -d $selectedDistro -e bash -lc 'echo WSL_OK; grep "^PRETTY_NAME=" /etc/os-release'
    $ubuntuExitCode = $LASTEXITCODE

    $ubuntuInfo | ForEach-Object {
        Write-Host $_
    }

    if ($ubuntuExitCode -ne 0) {
        Write-Fail "Ubuntu failed to start."
        exit 1
    }

    Write-Ok "Ubuntu is working."

    return $selectedDistro
}

function Ensure-LinuxTools {
    param([string]$Distro)

    Write-Step "Step 3: Check curl and zstd in Ubuntu"

    Invoke-WslBash $Distro 'command -v curl >/dev/null 2>&1'
    $hasCurl = ($LASTEXITCODE -eq 0)

    Invoke-WslBash $Distro 'command -v zstd >/dev/null 2>&1'
    $hasZstd = ($LASTEXITCODE -eq 0)

    if ($hasCurl -and $hasZstd) {
        Write-Ok "curl and zstd are installed."
        return
    }

    Write-Warn "Installing curl and zstd. Ubuntu may ask for sudo password."

    Invoke-WslBash $Distro 'sudo apt-get update && sudo apt-get install -y curl zstd'

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to install curl or zstd."
        exit 1
    }

    Write-Ok "curl and zstd are ready."
}

function Ensure-Ollama {
    param([string]$Distro)

    Write-Step "Step 4: Check Ollama"

    Invoke-WslBash $Distro 'command -v ollama >/dev/null 2>&1'

    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Ollama is installed."
    }
    else {
        Write-Warn "Ollama is not installed."

        if (Confirm-Yes "Install Ollama now?") {
            Write-Warn "Installing Ollama. Ubuntu may ask for sudo password."
            Invoke-WslBash $Distro 'curl -fsSL https://ollama.com/install.sh | sh'

            if ($LASTEXITCODE -ne 0) {
                Write-Fail "Failed to install Ollama."
                exit 1
            }

            Write-Ok "Ollama installed."
        }
        else {
            exit 1
        }
    }

    Write-Step "Step 5: Check Ollama API"

    if (Test-OllamaApi) {
        Write-Ok "Ollama API is running at $BaseUrl"
        return
    }

    Write-Warn "Ollama API is not running. Starting ollama serve in WSL."

    Invoke-WslBash $Distro 'mkdir -p ~/ollama-logs; nohup ollama serve > ~/ollama-logs/ollama.log 2>&1 &'

    $start = Get-Date
    $ready = $false

    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
        Start-Sleep -Seconds 2

        if (Test-OllamaApi) {
            $ready = $true
            break
        }

        Write-Host "Waiting for Ollama..."
    }

    if (-not $ready) {
        Write-Fail "Ollama did not start within timeout."
        Write-Host "Check log:"
        Write-Host "wsl -d $Distro -e bash -lc `"cat ~/ollama-logs/ollama.log`""
        exit 1
    }

    Write-Ok "Ollama API started."
}

function Stop-OllamaServer {
    param([string]$Distro)

    Write-Step "Final Step: Stop Ollama"

    if ($KeepOllama) {
        Write-Warn "KeepOllama is enabled. Ollama will keep running."
        return
    }

    Write-Warn "Stopping Ollama server in WSL..."

    Invoke-WslBash $Distro "sudo -n systemctl stop ollama 2>/dev/null || true; pkill -f 'ollama serve' 2>/dev/null || true; pkill -f 'ollama_llama_server' 2>/dev/null || true"

    Start-Sleep -Seconds 2

    if (Test-OllamaApi) {
        Write-Warn "Ollama may still be running. If it was started by Windows Ollama app or systemd, stop it manually if needed."
    }
    else {
        Write-Ok "Ollama has been stopped."
    }
}

function Get-LocalOllamaModels {
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/tags" -TimeoutSec 5

        if ($null -eq $response.models) {
            return @()
        }

        return @($response.models | ForEach-Object { $_.name })
    }
    catch {
        return @()
    }
}

function Pull-OllamaModel {
    param(
        [string]$Distro,
        [string]$ModelName
    )

    if (-not (Test-ModelName $ModelName)) {
        Write-Fail "Invalid model name: $ModelName"
        Write-Host "Examples: llama3.2:1b, qwen2.5:3b, gemma3:4b"
        exit 1
    }

    Write-Step "Pull model: $ModelName"

    Invoke-WslBash $Distro "ollama pull '$ModelName'"

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Failed to pull model: $ModelName"
        exit 1
    }

    Write-Ok "Model pulled: $ModelName"
}

function Select-Model {
    param([string]$Distro)

    Write-Step "Step 6: Select model"

    $models = Get-LocalOllamaModels

    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Cyan
    Write-Host "[1] Use an installed local Ollama model"
    Write-Host "[2] Enter a new model name and download it"
    Write-Host "[3] Enter a model name and test directly without downloading"
    Write-Host "[4] Environment check only"
    Write-Host "[5] Use mock model"

    $choice = Read-Host "Enter 1 / 2 / 3 / 4 / 5"

    switch ($choice) {
        "1" {
            if ($models.Count -eq 0) {
                Write-Warn "No local Ollama models found."
                Write-Host "Run again and choose [2] to download a model."
                exit 1
            }

            Write-Host ""
            Write-Host "Installed models:" -ForegroundColor Green

            for ($i = 0; $i -lt $models.Count; $i++) {
                $index = $i + 1
                Write-Host "[$index] $($models[$i])"
            }

            $modelChoice = Read-Host "Enter model number"

            if (-not ($modelChoice -as [int])) {
                Write-Fail "Invalid number."
                exit 1
            }

            $modelIndex = [int]$modelChoice

            if ($modelIndex -lt 1 -or $modelIndex -gt $models.Count) {
                Write-Fail "Model number out of range."
                exit 1
            }

            return "ollama:$($models[$modelIndex - 1])"
        }

        "2" {
            $newModel = Read-Host "Enter Ollama model name, for example llama3.2:1b or qwen2.5:3b"
            Pull-OllamaModel -Distro $Distro -ModelName $newModel
            return "ollama:$newModel"
        }

        "3" {
            $manualModel = Read-Host "Enter Ollama model name, for example llama3.2:1b"

            if (-not (Test-ModelName $manualModel)) {
                Write-Fail "Invalid model name."
                exit 1
            }

            return "ollama:$manualModel"
        }

        "4" {
            Write-Ok "Environment check completed."
            exit 0
        }

        "5" {
            return "mock"
        }

        default {
            Write-Fail "Invalid option."
            exit 1
        }
    }
}

function Run-Benchmark {
    param([string]$ModelArg)

    Write-Step "Step 7: Run benchmark"

    Write-Host "Model: $ModelArg" -ForegroundColor Green

    & python "src/run_benchmark.py" "--model" $ModelArg

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Benchmark failed."
        exit 1
    }

    Write-Ok "Benchmark completed."
}

function Generate-Report {
    Write-Step "Step 8: Generate report"

    & python "src/report_generator.py"

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Report generation failed."
        Write-Warn "If the error is about ':' in filename, patch report_generator.py to replace ':' with '_'."
        exit 1
    }

    Write-Ok "Report generated."
}

Write-Step "LLM Secret Guard Local Test Wizard"

Write-Host "Project path: $Root"
Write-Host "This script checks environment, starts Ollama, selects model, runs benchmark, and generates report."

Ensure-PythonDependencies

$selectedDistro = Ensure-WslAndUbuntu

Ensure-LinuxTools -Distro $selectedDistro

Ensure-Ollama -Distro $selectedDistro

if ($EnvOnly) {
    Write-Ok "Environment check completed."
    exit 0
}

$modelArg = Select-Model -Distro $selectedDistro

if (-not $SkipBenchmark) {
    Run-Benchmark -ModelArg $modelArg
}

if (-not $SkipReport) {
    Generate-Report
}

Stop-OllamaServer -Distro $selectedDistro

Write-Step "Done"

Write-Host "Model: $modelArg" -ForegroundColor Green
Write-Host "Results folder: results/"
Write-Host "Reports folder: reports/"
Write-Host ""
Write-Host "Open reports with:"
Write-Host "code reports"