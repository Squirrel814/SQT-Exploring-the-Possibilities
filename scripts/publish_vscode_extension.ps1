# Package and optionally publish sqt-grove VS Code extension.
# Usage:
#   .\scripts\publish_vscode_extension.ps1              # package only → .vsix
#   .\scripts\publish_vscode_extension.ps1 -Publish     # requires $env:VSCE_PAT

param(
    [switch]$Publish
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ExtDir = Join-Path $Root "widgets\vscode-sqt-grove"

Write-Host "Generating grove icon..."
python (Join-Path $Root "scripts\make_grove_icon.py")

Push-Location $ExtDir
try {
    if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
        throw "npx not found — install Node.js 20+"
    }

    Write-Host "Installing @vscode/vsce (local npx)..."
    npx --yes @vscode/vsce package

    $vsix = Get-ChildItem -Filter "sqt-grove-*.vsix" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $vsix) { throw "vsce package did not produce a .vsix file" }
    Write-Host "Packaged: $($vsix.FullName)"

    if ($Publish) {
        if (-not $env:VSCE_PAT) {
            throw @"
VSCE_PAT is not set.

Create a Personal Access Token at https://dev.azure.com (Marketplace → Manage → Access Tokens)
or https://marketplace.visualstudio.com/manage (Create Publisher → Access Token).

Then:
  `$env:VSCE_PAT = 'your-token'
  .\scripts\publish_vscode_extension.ps1 -Publish
"@
        }
        Write-Host "Publishing to Visual Studio Marketplace..."
        npx --yes @vscode/vsce publish -p $env:VSCE_PAT
        Write-Host "Published successfully."
    } else {
        Write-Host ""
        Write-Host "Manual install: code --install-extension $($vsix.FullName)"
        Write-Host "To publish: set VSCE_PAT then run with -Publish"
    }
}
finally {
    Pop-Location
}