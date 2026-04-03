$repoPath = "E:\Dev Microsoft\ChatGPT\RadiologyAI"
$backendPath = Join-Path $repoPath "backend"
$rootCelery = Join-Path $repoPath ".venv\Scripts\celery.exe"
$backendCelery = Join-Path $backendPath ".venv\Scripts\celery.exe"

if (Test-Path $rootCelery) {
  $celeryExe = $rootCelery
} elseif (Test-Path $backendCelery) {
  $celeryExe = $backendCelery
} else {
  Write-Error "No usable Celery executable found in .venv or backend\\.venv"
  exit 1
}

Set-Location $repoPath
$env:PYTHONPATH = $backendPath
& $celeryExe -A app.workers.celery_app.celery_app worker --pool=solo --loglevel=info
