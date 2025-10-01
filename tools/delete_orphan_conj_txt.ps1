$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath 'open_problems')) {
    Write-Output 'No open_problems directory found.'
    exit 0
}

$txtFiles = Get-ChildItem -Path 'open_problems' -Filter 'conj*.txt' -File -ErrorAction SilentlyContinue
if (-not $txtFiles) {
    Write-Output 'No matching files to evaluate.'
    exit 0
}

$deleted = @()
foreach ($f in $txtFiles) {
    $basename = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $mdPath = Join-Path -Path (Get-Location) -ChildPath ($basename + '.md')
    if (-not (Test-Path -LiteralPath $mdPath)) {
        Remove-Item -LiteralPath $f.FullName -Force
        $deleted += $f.FullName
    }
}

if ($deleted.Count -eq 0) {
    Write-Output 'No files deleted.'
} else {
    foreach ($d in $deleted) {
        Write-Output ("Deleted: $d")
    }
}

