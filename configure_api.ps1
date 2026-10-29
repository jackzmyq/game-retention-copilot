$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$secret = Read-Host 'Enter DeepSeek API Key (hidden input)' -AsSecureString
$secretPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPointer)
    if ([string]::IsNullOrWhiteSpace($plainKey) -or $plainKey.Contains("`n") -or $plainKey.Contains("`r")) { throw 'Invalid key.' }
    $content = "DEEPSEEK_API_KEY=$plainKey`nDEEPSEEK_MODEL=deepseek-flash`nDEEPSEEK_BASE_URL=https://api.deepseek.com`n"
    [System.IO.File]::WriteAllText((Join-Path $PSScriptRoot '.env'),$content,[System.Text.UTF8Encoding]::new($false))
    Write-Host 'Saved only to local .env (ignored by Git). Never share this file.'
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer)
    $plainKey = $null
    $content = $null
}
