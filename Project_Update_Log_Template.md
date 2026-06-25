# Project_Update_Log_Template.md

**For:** `project-logs/[Project-Name]_Project-Update.md`

Canonical copy also lives at: `C:\Projects\Grok-Agents\logs\shared-templates\templates\Project_Update_Log_Template.md`

---

### 1. Project-Specific Log Description + Notes  
**(For `project-logs/[Project-Name]_Project-Update.md`)**

**Purpose**  
This log captures the chronological, auditable history of a specific side-quest or curriculum project. It serves as the detailed "source of truth" for the project while the distilled, reusable knowledge is moved into the relevant Memory Islands with lightweight references only.

**What to Include in Each Entry**
- **SQT Timestamp** (required on every entry) — Use the format produced by `sqt_agent_clock.py` (e.g., `CyberSQRRL-SQT: Year 1, Cache | Truffle | 14:22:05 (SQT Agent Log)`).
- **Action / Contribution** — Concise description of what was done, decided, or handed off in this micro-step or phase segment.
- **Handoff / Next Agent** — Explicitly state who the work is being handed to (e.g., "→ Alex Pericles for micro-step security review" or "→ Zeenah for Phase Next-Step approval").
- **Options Presented (when applicable)** — Especially important for Cyber-SQRRL curriculum work. Briefly note the options considered before a decision.
- **Validation Gate Status** — Note whether the micro-step passed the Validation Gate checks or triggered a Revision Loop.
- **Open Questions or Risks** — Any blockers, security considerations, or decisions that need user or higher-level input.
- **Lightweight Reference (when distilling)** — If a reusable pattern is being identified, include the reference that will later go into the island (e.g., "See Post_Project_Summary for [ProjectName] for full details and contributions.").

**Core Rules**
- Never put full code, large examples, or complete module content in this log — only summaries and decisions.
- Every entry must be traceable via SQT stamp.
- At the end of a phase or project, this log (plus the final Post_Project_Summary) becomes the source material for distilling patterns into Memory Islands.
- User approves major phase transitions and final archive.

**End-of-Phase Ritual**  
When a phase or project concludes, create or update the corresponding `Post_Project_Summary.md` using the official template. Then distill only the reusable specialty knowledge into the relevant Memory Islands with lightweight references.

---

## Usage

Copy this template to `project-logs/[Project-Name]_Project-Update.md` for the active project.

### Log Entry Format (SQT-stamped, bullet or row style)

```
[AGENT-SQT: Year X, Lunation | Day | HH:MM:SS (SQT Agent Log)] 
Action/Contribution: ...
Handoff/Next: → [Agent] for ...
Validation Gate: Passed / Revision Loop triggered (reason)
Options: ...
Risks/Questions: ...
Lightweight Ref (if distilling): See Post_Project_Summary for [Project] for full details...
```

**Recommended:** Use `handoff_logger.pl` (enhanced) or `sqt_agent_clock.py --agent NAME` to generate the timestamp line, then append details.

Example entry:
```
CyberSQRRL-SQT: Year 1, Cache | Truffle | 14:22:05 (SQT Agent Log) | Action: Completed initial lab scaffold options for log parsing curriculum. Presented 3 progressive difficulty tracks. | Handoff: → Alex Pericles for micro-step 2.1 security review on input handling. | Validation Gate: Pending (submitted). | Options: Track A (beginner), B (intermediate), C (advanced with pcap). | See Post_Project_Summary for LogCurriculum-Phase2 for full options and decisions.
```

---

**End of Project_Update_Log_Template.md**

**Note:** This template enforces v2 Memory Ecosystem Map rules, SQT traceability, Validation Gate awareness, lightweight references, and island vs. project separation.