# Phase 2 Architecture Diagram (Initial)

## High-Level Data Flow (Mermaid)

```mermaid
graph TD
    A[SQT Unified Engine<br/>sqt_engine_unified.py] --> B[Holiday Detection<br/>sqt-holidays.sample.json]
    B --> C[Themes & Style<br/>sqt-themes.sample.json]
    C --> D[Messenger’s Circuit Engine<br/>Prompt Assembly]
    D --> E[Daily Bundle<br/>5 Elements JSON]
    E --> F[Widgets & Delivery]
    F --> G[Discord Bot]
    F --> H[Web Component<br/><sqt-grove-clock>]
    F --> I[VS Code Integration]
    F --> J[Static Export<br/>for GitHub Pages]
    G & H & I --> K[Community Layer<br/>lore-drop / Relay]
```

## Module Boundaries (Phase 2 Focus)

1. **Engine Layer (Jasper)**
   - Pure SQT calculation + holiday lookup
   - Headless first, JSON output
   - Sample data loading

2. **Themes & Prompts Layer (Crystal + Jasper)**
   - sqt-themes.json driven
   - Tiered prompt assembly
   - Style Guide enforcement

3. **Presentation Layer (Crystal)**
   - Widgets UI/UX
   - PWA
   - Mood board examples

4. **Curriculum Layer (Cyber-SQRRL)**
   - Squirrel Ops mappings
   - Lab injection into foraging

## Open Design Questions for Phase 2
- Coexistence of trimmed names vs legacy in public dashboard?
- How much state (evolving protagonist) to keep in memory vs files?
- Static export frequency vs live calls?

*Update this diagram as Phase 2 progresses. Lightweight Reference: See Post_Project_Summary for SQT-Exploring-the-Possibilities.*
