param([string]$PythonExe = "python")
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    & $PythonExe -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python venv creation failed. Install Python 3.12+ or pass -PythonExe.' }
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
    & uv --cache-dir "$PSScriptRoot\.cache\uv" pip install --python '.venv\Scripts\python.exe' -r requirements-lock.txt
} else {
    & '.\.venv\Scripts\python.exe' -m pip install -r requirements-lock.txt
}
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& '.\.venv\Scripts\python.exe' -X utf8 scripts/download_data.py
if ($LASTEXITCODE -ne 0) { throw 'Download failed.' }
& '.\.venv\Scripts\python.exe' -X utf8 scripts/build_pipeline.py
if ($LASTEXITCODE -ne 0) { throw 'Analysis failed.' }
& '.\.venv\Scripts\python.exe' -X utf8 -m src.reporting
if ($LASTEXITCODE -ne 0) { throw 'Report generation failed.' }
& '.\.venv\Scripts\python.exe' -X utf8 scripts/build_hr_pack.py
if ($LASTEXITCODE -ne 0) { throw 'HR introduction generation failed.' }
& '.\.venv\Scripts\python.exe' -X utf8 scripts/build_web.py
if ($LASTEXITCODE -ne 0) { throw 'Visitor demo export failed.' }
Write-Host 'Ready. Run .\start.ps1, then open http://127.0.0.1:8501'
