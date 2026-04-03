$repoPath = "E:\Dev Microsoft\ChatGPT\RadiologyAI"
$backendPath = Join-Path $repoPath "backend"
$rootPython = Join-Path $repoPath ".venv\Scripts\python.exe"
$backendPython = Join-Path $backendPath ".venv\Scripts\python.exe"

if (Test-Path $rootPython) {
  $pythonExe = $rootPython
} elseif (Test-Path $backendPython) {
  $pythonExe = $backendPython
} else {
  Write-Error "No usable Python executable found in .venv or backend\\.venv"
  exit 1
}

Set-Location $repoPath
& $pythonExe -m uvicorn --app-dir $backendPath app.main:app --reload --host 0.0.0.0 --port 9998
