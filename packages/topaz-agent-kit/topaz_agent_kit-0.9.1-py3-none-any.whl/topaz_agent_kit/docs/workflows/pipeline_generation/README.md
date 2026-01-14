# Pipeline Generation Workflow (Modular)

This directory contains the **modular pipeline generation workflow** — a structured, step-by-step process for creating production-ready pipelines in Topaz Agent Kit.

## Quick Start

**To invoke this workflow**: Ask the AI assistant to "follow the pipeline generation workflow" or reference the rule at `.cursor/rules/pipeline_generation.mdc`

## Directory Structure

```
pipeline_generation/
├── README.md                     # This file
├── step1_requirements.md         # Requirements gathering (comprehensive)
├── step2_design.md               # Workflow design & proposal
├── step3_refinement.md           # Interactive refinement
├── step4_generation.md           # File generation
├── step5_validation.md           # Validation & summary
├── reference_patterns.md         # Execution patterns reference
├── reference_hitl.md             # HITL gates reference
├── reference_jinja.md            # Jinja2 & variable syntax
├── reference_icons.md            # SVG icon generation
└── reference_troubleshooting.md  # Common errors and fixes
```

## Workflow Overview

| Step | Name | Key Activities | Checkpoint |
|------|------|----------------|------------|
| 1 | Requirements | Collect use case, agents, patterns, HITL, tools | 🔍 Requirements summary approval |
| 2 | Design | Finalize agents, design pattern structure, HITL gates | 🔍 Workflow proposal approval |
| 3 | Refinement | Incorporate feedback, resolve issues | 🔍 Final confirmation |
| 4 | Generation | Generate all config files, prompts, icons | 🔍 Review generated files |
| 5 | Validation | Validate variables, provide summary | 🔍 Completion confirmation |

## Files Generated Per Pipeline

| # | File Type | Location | Count |
|---|-----------|----------|-------|
| 1 | Pipeline config | `config/pipelines/{id}.yml` | 1 |
| 2 | Agent configs | `config/agents/{id}_{role}.yml` | N agents |
| 3 | Prompt templates | `config/prompts/{id}_{role}.jinja` | N agents |
| 4 | UI manifest | `config/ui_manifests/{id}.yml` | 1 |
| 5 | Pipeline icon | `ui/static/assets/{id}.svg` | 1 |
| 6 | Agent icons | `ui/static/assets/{id}_{role}.svg` | N agents |
| 7 | HITL templates | `config/hitl/{gate_id}.jinja` | As needed |

**Updated files:**
- `config/pipeline.yml`
- `config/ui_manifest.yml`
- `config/prompts/assistant_intent_classifier.jinja`

## Reference Documents

| Document | When to Use |
|----------|-------------|
| `reference_patterns.md` | Designing execution patterns (sequential, parallel, loop, etc.) |
| `reference_hitl.md` | Adding human-in-the-loop gates |
| `reference_jinja.md` | Variable syntax, filters, whitespace control |
| `reference_icons.md` | Generating SVG icons for pipeline and agents |
| `reference_troubleshooting.md` | Common errors, validation fixes, testing |

## Key Conventions

### Naming
- **Pipeline ID**: `snake_case` (e.g., `contract_analyzer`)
- **Agent ID**: `{pipeline_id}_{role}` (e.g., `contract_analyzer_extractor`)
- **Gate ID**: `{pipeline_id}_{purpose}` (e.g., `contract_analyzer_review`)

### Variable Syntax
- **Explicit** (preferred): `{{agent_id.field}}`
- **Simple**: `{{field}}` (only when unique)

### Base Path
Default: `src/topaz_agent_kit/templates/starters/ensemble/`

## Comparison with Legacy Workflow

This modular workflow replaces the monolithic legacy workflow with smaller, focused documents for better maintainability and AI context retention.

| Aspect | Legacy | Modular |
|--------|--------|---------|
| Total lines | ~4,113 | ~2,500 distributed |
| Main file | 1 large file | 1 orchestrator + 11 modules |
| Navigation | Scroll through sections | Direct file access |
| Maintainability | Edit 4000-line file | Edit specific step file |
| AI context | Often loses context | Each file fits in context |

## Archive

The original monolithic workflow has been archived for historical reference:
- **Location**: `docs/workflows/archive/pipeline_generation_workflow_legacy.md`
- **Status**: Superseded by this modular workflow
- **Use**: Reference only - do not use for new pipeline generation

