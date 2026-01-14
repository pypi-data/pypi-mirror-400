# ADR Builder

[![CI](https://github.com/LighthouseGlobal/adr-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/LighthouseGlobal/adr-builder/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/adr-builder.svg)](https://pypi.org/project/adr-builder/)

Create clear, consistent Architectural Decision Records (ADRs) from simple forms or YAML/JSON data — no coding required.

- Generates Markdown ADRs using the MADR standard
- Enforces structure and quality with built-in validation
- Works locally via an easy CLI, or in CI via GitHub Actions
- Stores ADRs in `docs/adr/` with automatic numbering, slugs, and an index

## Who is this for?

- Engineers, product managers, and stakeholders who need to record decisions
- Teams standardizing how ADRs are written and stored
- Anyone who wants a guided, non-technical way to produce ADRs

---

## Quick Start (No Coding)

Option A — Guided interactive flow (recommended):
1) Install (one-time)
   - macOS: `brew install pipx && pipx ensurepath`
   - All platforms (Python 3.9+): `pipx install adr-builder`
2) In your project folder, run:
   - `adr init` — sets up `docs/adr/` and defaults
   - `adr new` — guided prompts to create an ADR without editing files
3) Find your ADRs in `docs/adr/`

Option B — From a simple YAML file:
1) Create `criteria.yaml` like this:
```yaml
title: Database Selection
status: Proposed
authors: ["Jane Doe"]
tags: ["data", "persistence"]
context:
  background: "We need a primary OLTP database."
  constraints:
    - "Managed service"
    - "RTO <= 15m"
  drivers:
    - "Global availability"
    - "Operational simplicity"
options:
  - name: "PostgreSQL (AWS RDS)"
    pros: ["Mature ecosystem", "Managed backups"]
    cons: ["Vertical scaling limits"]
    risks: ["Cost at high scale"]
    score: 8
  - name: "CockroachDB Serverless"
    pros: ["Horizontal scale", "Strong consistency"]
    cons: ["Learning curve"]
    risks: ["Pricing predictability"]
    score: 7
decision:
  chosen: "PostgreSQL (AWS RDS)"
  rationale: "Best balance of maturity and ops simplicity."
consequences:
  positive: ["Familiar tooling", "Reduced ops overhead"]
  negative: ["Limited horizontal scale"]
references:
  links:
    - "https://adr.github.io/madr/"
```
2) Generate your ADR:
   - `adr generate --input criteria.yaml`
3) Your ADRs are created (e.g., `docs/adr/001-database-selection.md` and `.docx`).

Option C — In Pull Requests (GitHub Action):
- Add our CI workflow, commit `criteria.yaml`, and the action will generate/update ADRs automatically on PRs. See “CI Integration” below.

---

## Sample criteria.yml

Save this as `criteria.yml` (or `criteria.yaml`) and run `adr generate --input criteria.yml`:

```yaml
title: Database Selection
status: Proposed
authors: ["Jane Doe"]
tags: ["data", "persistence"]
context:
  background: "We need a primary OLTP database."
  constraints:
    - "Managed service"
    - "RTO <= 15m"
  drivers:
    - "Global availability"
    - "Operational simplicity"
options:
  - name: "PostgreSQL (AWS RDS)"
    pros: ["Mature ecosystem", "Managed backups"]
    cons: ["Vertical scaling limits"]
    risks: ["Cost at high scale"]
    score: 8
  - name: "CockroachDB Serverless"
    pros: ["Horizontal scale", "Strong consistency"]
    cons: ["Learning curve"]
    risks: ["Pricing predictability"]
    score: 7
decision:
  chosen: "PostgreSQL (AWS RDS)"
  rationale: "Best balance of maturity and ops simplicity."
consequences:
  positive: ["Familiar tooling", "Reduced ops overhead"]
  negative: ["Limited horizontal scale"]
references:
  links:
    - "https://adr.github.io/madr/"
```

---

## Installation

- Requirements: Python 3.9+ (or use Docker)
- Easiest: `pipx install adr-builder`
  - If you don't have pipx: `brew install pipx && pipx ensurepath` (macOS) or see https://pipx.pypa.io
- Verify: `adr --version`
- Word output requires the docx extra: `pipx install 'adr-builder[docx]'`

Docker (no Python needed):
```bash
docker run --rm -v "$PWD":/work -w /work ghcr.io/OWNER/adr-builder:latest adr --help
```

---

## Commands

- `adr init`
  - Scaffolds `docs/adr/`, default config, and template
- `adr new`
  - Interactive, step-by-step ADR creation (no editing files needed)
  - Generates both Markdown and Word outputs by default
  - Use `--format md` or `--format docx` for single format
- `adr generate --input criteria.yaml`
  - Creates or updates an ADR from YAML/JSON (Markdown and Word by default)
- `adr generate --input criteria.yaml --format md`
  - Generate only a Markdown output
- `adr generate --input criteria.yaml --format docx`
  - Generate only a Word document output for non-developers
- `adr validate --input criteria.yaml`
  - Checks structure, required fields, and statuses
  - Validates date format, option scores, URL formats, and decision consistency
  - Use `--directory` to specify project root for config loading
- `adr list`
  - Shows existing ADRs, numbers, and slugs
- `adr --version`
  - Shows the installed version

---

## Output Format

- Default template: MADR
- Default output: Markdown and Word (both)
- File naming: `NNN-slug.{md,docx}` (e.g., `001-database-selection.md`)
- Location: `docs/adr/`
- Index file: `docs/adr/index.md`
- Statuses: Proposed, Accepted, Superseded, Rejected (configurable)

Example generated ADR snippet:
```markdown
# Database Selection

- Status: Proposed
- Date: 2025-11-06
- Deciders: Jane Doe
- Tags: data, persistence

## Context and Problem Statement
We need a primary OLTP database.
Constraints:
- Managed service
- RTO <= 15m

Decision Drivers:
- Global availability
- Operational simplicity
```

---

## Templates

ADR Builder ships with three built-in templates:

| Template | Purpose | Audience |
|----------|---------|----------|
| `madr` | Standard MADR format (default) | General use |
| `hld` | High-Level Design ADRs | Architects, leadership |
| `lld` | Low-Level Design ADRs | Engineers, SRE, DevOps |

### Using Built-in Templates

```bash
# Use the default MADR template
adr generate --input criteria.yaml

# Use the HLD template for architectural decisions
adr generate --input criteria.yaml --template hld

# Use the LLD template for implementation decisions
adr generate --input criteria.yaml --template lld
```

Or set the default template in `.adr/adr.config.yaml`:
```yaml
template: hld  # or lld, madr
status_values: [Proposed, Accepted, Superseded, Rejected]
```

### Custom Templates

Support for custom templates via Jinja2:
```bash
adr generate --input criteria.yaml --template path/to/template.md.j2
```

---

## HLD and LLD Templates

For organizations with formal architecture review processes, ADR Builder supports a two-tier ADR structure:

- **HLD (High-Level Design)**: Strategic, architect-driven decisions about domains, patterns, and principles
- **LLD (Low-Level Design)**: Implementation-focused, engineer-driven decisions about specific technologies and configurations

### When to Use Each Template

| Use HLD When... | Use LLD When... |
|-----------------|-----------------|
| Defining system domains and boundaries | Specifying infrastructure and services |
| Choosing architectural patterns | Selecting specific technologies |
| Setting guiding principles | Defining operational configurations |
| Evaluating strategic alternatives | Documenting security controls |
| Establishing governance processes | Planning rollout and testing |

### HLD Template Sections

The HLD template is designed for architect-driven decisions:

```
- ADR Number, Status, Date, Authors, Reviewers, Tags
- Context and Problem Statement (with drivers and constraints)
- Decision (strategic approach)
- Rationale
- Alternatives Considered
- Consequences / Implications
- Links / Diagrams
- Stakeholders
- Assumptions
- Next Steps
```

### LLD Template Sections

The LLD template is designed for engineer-driven implementation details:

```
- ADR Number, Status, Date, Authors, Parent ADR, Reviewers, Tags
- Context (links to parent HLD)
- Decision Summary
- Detailed Rationale
- Component Design & Diagrams
- Configuration & Operational Details
- Security Considerations
- Testing / Validation
- Rollout & Rollback Plan
- Dependencies
- Next Steps
```

### HLD Example (criteria.yaml)

```yaml
title: "Platform v1 — High-Level Architecture"
adr_number: "ADR-20260106-01"
status: Proposed
authors: ["Jane Doe <jane@example.com>"]
reviewers: ["Architecture Lead", "Engineering Manager"]
tags: ["architecture", "platform"]

context:
  background: |
    We need a scalable, secure platform architecture that meets
    business requirements for scale and extensibility.
  drivers:
    - "Deliver a modular, API-first architecture"
    - "Favor secure-by-design decisions"
  constraints:
    - "Must support cloud deployment"
    - "Must enable independent scaling"

decision:
  chosen: "Modular, API-first design"
  rationale: |
    Adopt a modular design with two domains:
    1. **Frontend** — UI, API gateway, auth
    2. **Backend** — Processing, data services

rationale:
  - "Modularity isolates concerns and enables independent scaling"
  - "API-first reduces coupling"

alternatives:
  - name: "Monolithic architecture"
    pros: ["Simpler initial deployment"]
    cons: ["Scaling limitations", "Tight coupling"]

consequences:
  positive: ["Clear ownership boundaries", "Independent deployments"]
  negative: ["Increased operational complexity"]

stakeholders:
  - "Architecture Lead — primary reviewer"
  - "Jane Doe — owner"

assumptions:
  - "Cloud infrastructure is available"
  - "Team has containerization experience"

next_steps:
  - "Create LLD ADR with implementation details"
  - "Attach architecture diagrams"
  - "Request stakeholder review"

references:
  links: ["https://adr.github.io/madr/"]
  related_adrs: ["ADR-20260106-02 (LLD - child)"]
```

### LLD Example (criteria.yaml)

```yaml
title: "Platform v1 — Low-Level Implementation"
adr_number: "ADR-20260106-02"
status: Proposed
authors: ["John Smith <john@example.com>"]
parent_adr: "ADR-20260106-01 (High-Level Architecture)"
reviewers: ["Architecture Lead", "SRE Team", "Security"]
tags: ["implementation", "infrastructure"]

context:
  background: |
    This ADR captures implementation patterns for Platform v1,
    implementing the High-Level ADR (ADR-20260106-01).
  constraints:
    - "Must align with HLD decisions"
    - "Must meet security requirements"

decision:
  chosen: "Kubernetes-based implementation"
  rationale: |
    - **Compute:** Kubernetes (AKS) for container orchestration
    - **Data:** Managed database services
    - **Identity:** OAuth2/OIDC for authentication
    - **IaC:** Terraform for infrastructure

options:
  - name: "Kubernetes-based implementation"
    pros: ["Autoscaling", "Container isolation", "Managed services"]

rationale:
  - name: "Kubernetes"
    description: "Provides autoscaling and reduces operational overhead"
  - name: "Managed databases"
    description: "Built-in backups and reduced ops burden"

components:
  - name: "Frontend Services"
    responsibilities: ["API gateway", "Authentication", "UI hosting"]
    services: ["API Gateway", "Auth service", "Static hosting"]
  - name: "Backend Services"
    responsibilities: ["Data processing", "Model serving"]
    services: ["Worker pods", "GPU nodes", "Message queues"]

operations:
  regions: ["Primary region", "DR region"]
  networking: ["Private subnets", "Network policies", "Service mesh"]
  scaling: ["HPA for services", "Cluster autoscaler"]
  monitoring: ["Prometheus metrics", "Distributed tracing", "Alerting"]
  backup: ["Daily snapshots", "Cross-region replication"]

security:
  threat_model: "Encryption at rest/transit, least privilege access"
  secrets: "Vault for secrets management with rotation"
  compliance: ["SOC2", "GDPR"]
  review: "Security review required before production"

testing:
  - "Unit and integration tests"
  - "Load testing with SLO targets"
  - "Staging environment validation"

rollout:
  strategy: "Canary deployments with progressive rollout"
  rollback: "Automated rollback on SLO breach"
  feature_flags: ["New features behind flags"]

dependencies:
  - "Parent HLD ADR"
  - "Cloud infrastructure setup"
  - "Security approvals"

next_steps:
  - "Create IaC templates"
  - "Set up CI/CD pipelines"
  - "Submit for security review"
```

### Parent-Child ADR Linking

LLD ADRs can reference their parent HLD using the `parent_adr` field:

```yaml
# In LLD criteria
parent_adr: "ADR-20260106-01 (Platform v1 — High-Level Architecture)"
```

HLD ADRs can reference child LLDs in the `related_adrs` field:

```yaml
# In HLD criteria
references:
  related_adrs:
    - "ADR-20260106-02 (LLD - Implementation)"
```

---

## CI Integration (GitHub Action)

Add `.github/workflows/adr.yml`:
```yaml
name: ADR
on:
  pull_request:
    paths:
      - 'criteria/*.yaml'
jobs:
  build-adr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - run: pipx install adr-builder
      - run: adr init
      - run: adr generate --input criteria/main.yaml
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore(adr): generate ADR from criteria"
```

---

## Troubleshooting

- “Command not found: adr”
  - Ensure `pipx ensurepath` was run, then open a new terminal
- "Python not found"
  - Install Python 3.9+ or use Docker
- Validation errors
  - Run `adr validate --input criteria.yaml` to see what to fix

---

## Contributing

- Issues and PRs welcome
- Install dev dependencies: `pip install -e ".[dev]"`
- Run tests: `pytest`
- Lint: `ruff check adr_builder/`
- Type check: `mypy adr_builder/`

## Release process

We publish to PyPI via GitHub Actions using version tags.

1) Bump the version in `pyproject.toml` and `adr_builder/__init__.py`
2) Commit the change to `main`:
   ```bash
   git add pyproject.toml adr_builder/__init__.py
   git commit -m "chore(release): bump version to X.Y.Z"
   git push origin main
   ```
3) Create and push a tag (must be new):
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
4) Confirm the workflow ran:
   - GitHub → Actions → “Publish to PyPI” → tag `vX.Y.Z`
5) Confirm on PyPI:
   - https://pypi.org/project/adr-builder/

Notes:
- The `Publish to PyPI` workflow runs on tags matching `v*`.

## License

MIT
