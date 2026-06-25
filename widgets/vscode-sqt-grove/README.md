# SQT Grove — VS Code Extension

Live Squirrel Quantum Time status bar + insert **Messenger's Circuit** bundles into your editor.

## Features

- Status bar: Moon/day labels, holiday badge, major events show `$(star-full)`
- **Insert Messenger's Circuit Bundle** — markdown or language-aware comment blocks
- **Insert Foraging Idea** — quick daily action line
- Optional **Squirrel Ops** lab injection (`sqtGrove.squirrelOps`)
- Circuit modes: `standard`, `teaser`, `whisper`, `ceremonial`, `storytelling`, `project-deep`

## Development

Press **F5** with this folder open (Extension Development Host). See `.vscode/launch.json`.

```powershell
# From repo root (recommended):
.\scripts\publish_vscode_extension.ps1

# Or manually:
cd widgets/vscode-sqt-grove
npx @vscode/vsce package      # → sqt-grove-0.3.1.vsix
code --install-extension sqt-grove-0.3.1.vsix
```

## Configuration

| Setting | Default | Notes |
|---------|---------|-------|
| `sqtGrove.enginePath` | *(workspace search)* | Path to `sqt_engine_unified.py` |
| `sqtGrove.staticJsonPath` | — | Use `circuit-current.json` instead of subprocess |
| `sqtGrove.insertFormat` | `markdown` | `markdown` or `comment-block` |
| `sqtGrove.circuitMode` | `standard` | Passed as `--circuit-mode` |
| `sqtGrove.projectContext` | — | For `project-deep` mode |
| `sqtGrove.squirrelOps` | `false` | Engine `--squirrel-ops` |

## Marketplace publish (manual token step)

1. Create publisher **squirrel814** at https://marketplace.visualstudio.com/manage
2. Generate a Personal Access Token (Marketplace → **Manage** → **Access Tokens**)
3. In PowerShell:

```powershell
$env:VSCE_PAT = 'your-marketplace-token'
cd C:\Users\Inter\Documents\GitHub\SQT-Exploring-the-Possibilities
.\scripts\publish_vscode_extension.ps1 -Publish
```

4. Verify listing icon + README; link to live PWA demo

## License

MIT — see repo root `LICENSE`.