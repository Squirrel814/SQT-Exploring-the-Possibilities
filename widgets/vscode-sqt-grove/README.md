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

```bash
npm install -g @vscode/vsce   # once
vsce package                  # produces sqt-grove-0.3.0.vsix
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

## Marketplace publish (manual)

1. Create publisher at https://marketplace.visualstudio.com/manage
2. `vsce login squirrel814`
3. `vsce publish` from this directory
4. Verify icon + README render; link to live PWA demo

## License

MIT — see repo root `LICENSE`.