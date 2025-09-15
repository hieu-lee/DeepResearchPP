param(
  [string]$Prompt = "Say 'hello' and include your model name."
)

if (-not $env:OPENAI_API_KEY -or [string]::IsNullOrWhiteSpace($env:OPENAI_API_KEY)) {
  Write-Error "OPENAI_API_KEY environment variable is not set."
  exit 1
}

$headers = @{
  "Authorization" = "Bearer $env:OPENAI_API_KEY"
  "Content-Type" = "application/json"
}

$body = @{
  model = "gpt-4o-mini"
  messages = @(
    @{ role = "user"; content = $Prompt }
  )
  temperature = 0
} | ConvertTo-Json -Depth 6

try {
  $response = Invoke-RestMethod \
    -Uri "https://api.openai.com/v1/chat/completions" \
    -Headers $headers \
    -Method Post \
    -Body $body \
    -TimeoutSec 30

  $content = $response.choices[0].message.content
  if ($content) {
    Write-Output $content
  } else {
    Write-Host ($response | ConvertTo-Json -Depth 10)
  }
}
catch {
  Write-Error $_
  if ($_.Exception.Response -and $_.Exception.Response -is [System.Net.HttpWebResponse]) {
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errBody = $reader.ReadToEnd()
    Write-Host "Error body:" -ForegroundColor Yellow
    Write-Host $errBody
  }
  exit 2
}

