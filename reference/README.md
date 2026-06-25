# Engine Reference (This Repository Only)

**`sqt_engine_2.py`** in this folder is a **read-only snapshot** copied from the upstream Squirrel-Quantum-Time project. It is the precision and naming source of truth for this exploration repo.

**`sqt_engine_unified.py`** (repo root) is the **headless rewrite** of that engine for SQT-Exploring-the-Possibilities. It adds:

- Holiday + theme loading
- Messenger's Circuit `generate_bundle()` output
- Widget-ready JSON contract
- CLI (`--json`, `--bundle`, `--holiday`)

This exploration repo does **not** modify the upstream Squirrel-Quantum-Time repository. Any engine evolution happens here first; upstream adoption is a separate decision.