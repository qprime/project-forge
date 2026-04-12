# Project Ecosystem Dashboard

**Generated:** 2026-04-12 | **Registry:** 16 projects | **Baseline:** 2026-04-05

---

## Overview

| Project | Type | Language | Status | Last Active | Commits | Open Issues |
|---------|------|----------|--------|-------------|---------|-------------|
| **mill_ui** | CAM pipeline | Python | Active | 2026-04-08 | 469 | 16 |
| **TenneCNC_LLC** | Document corpus | Markdown | Active | 2026-04-12 | 48 | 0 |
| **homenet** | Infrastructure ops | Python | Active | 2026-04-12 | 12 | 3 |
| **penumbra-poc** | ML pipeline POC | Python | Active | 2026-04-12 | 11 | 1 |
| **project-forge** | Meta/bootstrap | YAML/MD | Active | 2026-04-12 | 3 | 0 |
| **infrastructure** | Service mgmt | Shell/Python | Maintained | 2026-04-06 | 5 | 0 |
| **SAK-router** | Microservice | Python | Maintained | 2026-04-06 | 13 | 0 |
| **artifact-classifier** | Microservice | Python | Maintained | 2026-04-06 | 4 | 1 |
| **sdb-auditor** | Governance tool | Python | Skeleton | 2026-04-06 | 2 | 1 |
| **turnstile** | Chat UI | TypeScript | Dormant | 2025-12-15 | 14 | 0 |
| **artifact-assembler** | Microservice | Python | Dormant | 2025-12-16 | 7 | 4 |
| **orchestrator** | Microservice | Python | Dormant | 2025-12-16 | 12 | 0 |
| **session-manager** | Microservice | Python | Dormant | 2025-12-16 | 9 | 0 |
| **artifact-engine** | Microservice | Python | Dormant | 2025-12-13 | 5 | 2 |
| **integration-tests** | Test suite | Python | Dormant | 2025-12-10 | 5 | 0 |
| **cliff_ai** | AI orchestration | Python | Remote only | — | — | — |

---

## Claude Code Configuration Maturity

| Project | CLAUDE.md | Skills | Invariants | Hooks | Baseline Version |
|---------|-----------|--------|------------|-------|------------------|
| **mill_ui** | Yes | 13 | 19 files | Yes | 2026-04-05 |
| **homenet** | Yes | 8 | 8 files | Yes | — |
| **penumbra-poc** | Yes | 7 | 4 files | Yes | — |
| **TenneCNC_LLC** | Yes | 12 | 1 file | No | 2026-04-05 |
| **project-forge** | Yes | 14 | 1 file | No | — |
| **infrastructure** | — | — | — | — | — |
| **turnstile** | — | — | — | — | — |
| **artifact-assembler** | — | — | — | — | — |
| **SAK-router** | — | — | — | — | — |
| **session-manager** | — | — | — | — | — |
| **orchestrator** | — | — | — | — | — |
| **artifact-engine** | — | — | — | — | — |
| **integration-tests** | — | — | — | — | — |
| **artifact-classifier** | — | — | — | — | — |
| **sdb-auditor** | — | — | — | — | — |
| **cliff_ai** | — | — | — | — | — |

---

## Codebase Scale

| Project | Source Files | Test Files | Source LoC | Docs (MD) |
|---------|-------------|------------|------------|-----------|
| **mill_ui** | 276 .py | 99 | ~76,000 | 104 |
| **TenneCNC_LLC** | 2 .py (MCP) | — | — | 117 |
| **homenet** | 20 .py | — | ~3,400 | 56 |
| **penumbra-poc** | 22 .py | 8 | ~2,800 | 19 |
| **SAK-router** | 18 .py | 9 | — | 4 |
| **artifact-classifier** | 17 .py | 3 | — | 8 |
| **artifact-engine** | 11 .py | 4 | — | 11 |
| **session-manager** | 7 .py | 4 | — | 3 |
| **orchestrator** | 7 .py | 4 | — | 4 |
| **artifact-assembler** | 5 .py | 4 | — | 4 |
| **integration-tests** | 6 .py | 6 | — | 4 |
| **turnstile** | 15 .ts/.tsx | — | — | 11 |
| **infrastructure** | 6 .py + shell | — | ~1,150 | 3 |
| **sdb-auditor** | 5 .py (stubs) | — | — | 7 |
| **project-forge** | — | — | — | 19 |

---

## Architecture Map

### Tier 1: Flagship Projects (full Claude Code config, active development)

**mill_ui** — Compiler-style CAM pipeline
```
PML/YAML → LayoutAST → RemovalIntent IR → CAM Planner → G-code + SVG
```
- 19 invariant files, 99 test files, ~2200 tests
- Frozen dataclasses, domain algebra, interface-first joinery
- Assembly system: box, carcass, cubby, beam
- Blueprint export (SVG/PDF), MCP server integration

**homenet** — Operator-centric infrastructure platform
```
Discovery → Inventory → Provisioning → Monitoring
```
- 14 tools (discover, provision, backup, PKI, service_ctl, etc.)
- SSH wrapper with session logging, dry-run safety
- Internal PKI (step-ca), Caddy TLS proxies
- Manages: eqbeelink1, skytech, macm2, orangepiaipro

**penumbra-poc** — Staged ML pipeline for log scanning
```
CSV Ingest → PolarContour IR → Completion (5 baselines) → Evaluation → SVG
```
- Sawmill hidden-side estimation (90-120 degree occlusion)
- Stage 1 complete (geometric baselines), Stage 2/3 planned
- Target: CPU-only, <50ms per log

### Tier 2: Document & Business Intelligence

**TenneCNC_LLC** — ADI-structured document corpus
```
Abstract (theory) → Domain (applications) → Implementation (prompts)
```
- 117 markdown documents across 3 ADI layers
- Multi-persona staff system (6 personas with shared business context)
- Whitepaper voice enforcement, cross-reference protocol
- SDB (Software-Defined Business) framework documentation

**project-forge** — Meta-project / bootstrap orchestrator
```
Registry → Survey → Profile → Drift → Rebase
```
- Capability baseline with 7 always-on + 12 conditional capabilities
- 14 skills covering full development workflow
- This dashboard is its first derived artifact

### Tier 3: Turnstile Chat Stack (6 microservices, dormant since Dec 2025)

```
Turnstile (UI) → Backend Proxy
                    |
              Orchestrator (:3006)
             /        |        \
   SAK-Router   Session-Mgr  Artifact-Assembler
    (:3005)      (:3004)        (:3003)
        |                          |
    Model Gateway         Artifact-Engine
     (Cortex)               (:3002)
```

| Service | Purpose | Modules | Tests |
|---------|---------|---------|-------|
| turnstile | React carousel UI + Express proxy | 15 TS | — |
| SAK-router | Deterministic routing, model gateway | 18 py | 9 |
| orchestrator | YAML pipeline executor | 7 py | 4 |
| session-manager | Turn storage, distillation | 7 py | 4 |
| artifact-assembler | Multi-engine doc aggregation | 5 py | 4 |
| artifact-engine | Registry-based artifact storage | 11 py | 4 |
| integration-tests | Contract + E2E tests | 6 py | 6 |

All Python services: FastAPI + uvicorn + httpx + pydantic. None have Claude Code config.

### Tier 4: Supporting Projects

| Project | Purpose | State |
|---------|---------|-------|
| **infrastructure** | Systemd units, backup scripts, microservice supervisor | Operational, no Claude config |
| **artifact-classifier** | LLM-powered artifact classification (FastAPI) | Complete, no Claude config |
| **sdb-auditor** | Git repo scanning + semantic drift detection | Skeleton (stubs only) |
| **cliff_ai** | AI management/memory framework | Remote only, no local path |

---

## Project Families

| Family | Projects | Shared Patterns |
|--------|----------|-----------------|
| **Manufacturing** | mill_ui, penumbra-poc | Pipeline IR, frozen dataclasses, coordinate invariants |
| **Business/Docs** | TenneCNC_LLC, sdb-auditor | ADI taxonomy, SDB framework, governance |
| **Chat/AI Stack** | turnstile, orchestrator, SAK-router, session-manager, artifact-assembler, artifact-engine, artifact-classifier, integration-tests | FastAPI microservices, deterministic routing |
| **Infrastructure** | homenet, infrastructure | Tool-first ops, systemd, backup orchestration |
| **Meta** | project-forge, cliff_ai | Cross-project intelligence, capability baselines |

---

## Health Check (FG-6)

| Status | Count | Projects |
|--------|-------|----------|
| OK (path exists) | 15 | all local projects |
| REMOTE ONLY | 1 | cliff_ai |
| BROKEN | 0 | — |

---

## Bootstrap Coverage

| Status | Count | Projects |
|--------|-------|----------|
| Baselined (2026-04-05) | 2 | mill_ui, TenneCNC_LLC |
| Configured (no version) | 3 | homenet, penumbra-poc, project-forge |
| Unconfigured | 11 | infrastructure, turnstile, all Turnstile stack, sdb-auditor, cliff_ai |

---

## Activity Timeline

```
2025-09  mill_ui first commit
2025-11  infrastructure first commit
2025-12  Turnstile stack buildout (7 repos created in ~10 days)
         TenneCNC_LLC, artifact-engine, artifact-classifier, sdb-auditor initialized
2025-12  Turnstile stack goes dormant (last commits Dec 10-16)
2026-03  homenet first commit, mill_ui measurement/assembly features
2026-04  project-forge created, baseline extracted from TenneCNC_LLC
         homenet: PKI deployment, CloudCLI, Whisper migration
         penumbra-poc: full Stage 1 implementation (11 commits in 2 days)
         TenneCNC_LLC: personal domain, config rebase
         infrastructure: service path rebase, Turnstile/Paperless units
```
