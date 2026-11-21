# Copies the files the Space needs into the Space repository folder.
# Usage (from the repo root):  .\deploy\space\sync.ps1 -SpaceDir ..\canemitra-space
param([Parameter(Mandatory = $true)][string]$SpaceDir)

if (-not (Test-Path $SpaceDir)) { throw "Space folder not found: $SpaceDir" }

# Start clean (keep the .git folder)
Get-ChildItem $SpaceDir -Force | Where-Object { $_.Name -ne ".git" } | Remove-Item -Recurse -Force

Copy-Item -Recurse app (Join-Path $SpaceDir "app")
Copy-Item -Recurse prompts (Join-Path $SpaceDir "prompts")
New-Item -ItemType Directory (Join-Path $SpaceDir "data") | Out-Null
foreach ($f in "chunks.json", "records.json", "sample_records.json") {
    Copy-Item (Join-Path "data" $f) (Join-Path $SpaceDir "data")
}
Copy-Item requirements.txt $SpaceDir
Copy-Item deploy\space\Dockerfile $SpaceDir
Copy-Item deploy\space\README.md $SpaceDir

Get-ChildItem $SpaceDir -Recurse -Directory -Force -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "Space folder is ready: $SpaceDir"