# Career Orchestrator: Product Requirements and Engineering Specification

**SAP Hackfest 2026, Grand Finale, Theme 2: Inclusive Workforce** | Team: The Creative Coders | Version 1.0 | Prepared Saturday 31 October 2026 | Engineering freeze: Tuesday 3 November 2026, 12:00 IST | Finale: Wednesday 4 November 2026

**Status of this document.** This is the authoritative engineering specification for the prototype. Where it conflicts with the earlier concept deck, this document wins (differences are listed in section 2.3). All data, personas and numbers in examples are synthetic. All scoring weights, thresholds and targets are provisional engineering choices, not validated findings.

**Evidence labels used throughout.**

| Label | Meaning |
|---|---|
| **[V]** | Verified: read directly from the cited official source during preparation of this document (sources in section 55) |
| **[J]** | Engineering judgment: our reasoned recommendation, not a sourced fact |
| **[U]** | Unverified: could not be confirmed from an accessible source; must be checked by the named owner before relying on it |
| **[S]** | Stated in the supplied competition handbook or team concept deck |

**Reading guide.** Part I defines the product. Part II records research and architecture decisions. Part III specifies the AI and data engineering. Part IV specifies the application. Part V is the execution plan. Each developer should read Part I, section 16-17, their own subsection of 45, and the contracts in 24 and 35. Companion files in the repository (contracts/openapi.yaml, contracts/models.py, data/fixtures/, AGENTS.md, docs/MILESTONES.md, docs/DEMO_CHECKLIST.md) are generated from or consistent with this document.

\newpage
