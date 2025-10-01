$ErrorActionPreference = 'Stop'

$pattern = '**message**: Problem too difficult!'

$files = Get-ChildItem -Path . -Filter 'conj*.md' -File
$deleted = @()

foreach ($f in $files) {
    if (Select-String -Path $f.FullName -SimpleMatch -Quiet -Pattern $pattern) {
        Remove-Item -LiteralPath $f.FullName -Force
        $deleted += $f.FullName
    }
}

if ($deleted.Count -eq 0) {
    Write-Output 'No matching files deleted.'
} else {
    foreach ($d in $deleted) {
        Write-Output ("Deleted: $d")
    }
}

