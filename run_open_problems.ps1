Param(
    [int[]]$Indices = 51..57,
    [switch]$Sequential
)

$ErrorActionPreference = 'Stop'

# Ensure we run from the repo root (where this script lives)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# Activate the virtual environment if available
$activate = Join-Path $root '.venv\Scripts\Activate.ps1'
if (Test-Path $activate) {
    . $activate
} else {
    Write-Warning "Activation script not found at $activate; proceeding with venv python path."
}

# Resolve venv Python
$venvPy = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) {
    throw "Venv python not found at $venvPy. Create the venv or adjust the path."
}

# Validate input files exist
foreach ($i in $Indices) {
    $inFile = Join-Path $root ("open_problems/conj{0}.txt" -f $i)
    if (-not (Test-Path $inFile)) {
        throw "Missing input file: $inFile"
    }
}

if ($Sequential) {
    Write-Host "Running jobs sequentially..."
    $failed = @()
    foreach ($i in $Indices) {
        $inFile = Join-Path $root ("open_problems/conj{0}.txt" -f $i)
        $outFile = "conj{0}.md" -f $i
        $args = @('-m','backend.cli','--open-problem', "-f=$inFile", "-o=$outFile")
        Write-Host ("Starting conj{0}..." -f $i)
        & $venvPy @args
        $code = $LASTEXITCODE
        if ($code -ne 0) {
            Write-Error ("conj{0} exited with code {1}" -f $i, $code)
            $failed += @{ Index = $i; ExitCode = $code }
        } else {
            Write-Host ("conj{0} completed successfully." -f $i)
        }
    }

    if ($failed.Count -gt 0) {
        $summary = $failed | ForEach-Object { "conj$($_.Index):$($_.ExitCode)" }
        throw ("One or more jobs failed (sequential): " + ($summary -join ', '))
    }

    Write-Host "All jobs completed successfully (sequential)."
} else {
    # Start all processes in parallel
    $procs = @()
    foreach ($i in $Indices) {
        $inFile = Join-Path $root ("open_problems/conj{0}.txt" -f $i)
        $outFile = "conj{0}.md" -f $i
        $args = @('-m','backend.cli','--open-problem', "-f=$inFile", "-o=$outFile")
        $p = Start-Process -FilePath $venvPy -ArgumentList $args -WorkingDirectory $root -NoNewWindow -PassThru
        Write-Host ("Started conj{0}: PID {1}" -f $i, $p.Id)
        $procs += $p
    }

    # Wait for completion
    Wait-Process -Id ($procs | ForEach-Object Id)

    # Check exit codes and report
    $failed = @()
    foreach ($p in $procs) {
        $p.Refresh()
        if ($p.ExitCode -ne 0) {
            $failed += $p
            Write-Error ("Process PID {0} exited with code {1}" -f $p.Id, $p.ExitCode)
        } else {
            Write-Host ("Process PID {0} completed successfully." -f $p.Id)
        }
    }

    if ($failed.Count -gt 0) {
        throw ("One or more jobs failed: " + (($failed | ForEach-Object Id) -join ', '))
    }

    Write-Host "All jobs completed successfully."
}
