param(
  [switch]$Force
)

# Sets the current user's OPENAI_API_KEY from the system-level (Machine) value.
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/set-openai-key-from-system.ps1
#   # or
#   .\scripts\set-openai-key-from-system.ps1

function Get-SystemOpenAIKey {
  $machine = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'Machine')
  if ([string]::IsNullOrWhiteSpace($machine)) {
    return $null
  }
  return $machine
}

function Get-UserOpenAIKey {
  $user = [System.Environment]::GetEnvironmentVariable('OPENAI_API_KEY', 'User')
  if ([string]::IsNullOrWhiteSpace($user)) {
    return $null
  }
  return $user
}

$systemKey = Get-SystemOpenAIKey
if (-not $systemKey) {
  Write-Error "System-level (Machine) OPENAI_API_KEY is not set. Nothing to copy."
  exit 1
}

$userKey = Get-UserOpenAIKey
if ($userKey -and -not $Force) {
  if ($userKey -eq $systemKey) {
    Write-Host "User OPENAI_API_KEY already matches the system value." -ForegroundColor Green
    exit 0
  }
  Write-Warning "User OPENAI_API_KEY is already set and differs from the system value. Use -Force to overwrite."
  Write-Host "Current user value (first 6 chars): '" ($userKey.Substring(0, [Math]::Min(6, $userKey.Length))) "...'"
  exit 2
}

try {
  [System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', $systemKey, 'User')
  # Also set for this PowerShell session so immediate commands can use it
  $env:OPENAI_API_KEY = $systemKey
  Write-Host "Set user OPENAI_API_KEY from system value (length=$($systemKey.Length))." -ForegroundColor Green
  Write-Host "You may need to restart apps/terminals for the change to take effect."
  exit 0
}
catch {
  Write-Error "Failed to set user OPENAI_API_KEY: $_"
  exit 3
}

