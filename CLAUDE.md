Perfect, I have enough context to craft a solid `CLAUDE.md` for your backend. Let me synthesize this into a comprehensive guide.

---

```markdown
# CLAUDE.md — RadPort Backend

> This file is the source of truth for Claude Code working on this repo.
> Read it fully before writing a single line of code or making any edit.

---

## What Is RadPort?

**RadPort** is an AI-assisted radiology documentation platform built for the MENA healthcare market.

It is **not** a diagnostic AI. It does not read or interpret medical images. It is a structured documentation workflow that helps radiologists produce faster, more consistent, fully physician-signed reports — while maintaining complete legal accountability and a tamper-proof audit trail.

**One-line pitch:** RadPort gives radiologists a structured checklist, an AI-drafted report, and a signed, audit-ready output — in a fraction of the time.

**This repo is the backend.** It powers the RadPort application: user authentication, study metadata, checklist templates, AI-assisted report drafting via LLM integration, PACS proxy authentication, and audit logging. The frontend is a separate static site deployed on Cloudflare Pages.

---

## Current Project State

This is a **Django + Django REST Framework monolith** running on a bare-metal server. The project is in active development by a **solo developer** — there is no team, no PRs, no code review process. All commits go directly to `main`.

The product is currently a **demo/MVP**. Compliance (HIPAA, PDPL), production hardening, infrastructure-as-code, and automated CI/CD are deferred to later stages. The current focus is feature correctness and workflow completion for chest X-ray studies.

### Current Scope (What This Repo Handles)

| In Scope | Deferred / Out of Scope |
|---|---|
| User authentication (JWT) | HIPAA/PDPL compliance controls |
| User token management | Automated CI/CD pipeline |
| Checklist template storage & retrieval | Infrastructure as Code |
| LLM integration (Anthropic) for report drafting | Multi-modality support (chest X-ray only) |
| PACS proxy authentication | Automated test suites |
| PDF report generation | API versioning |
| Basic audit logging | Horizontal scaling / caching |
| REST API (single version) | FHIR/HL7 integrations |

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3 | — |
| Framework | Django + Django REST Framework | Monolithic architecture |
| Database | PostgreSQL | No caching layer (Redis, etc.) |
| LLM Provider | Anthropic | Prompt structure to be integrated soon |
| File Storage | Local / server filesystem | PDF reports stored server-side |
| Deployment | Bare-metal server | Manual deployment process |
| Auth | JWT (djangorestframework-simplejwt or similar) | Token-based, no OAuth2 |

**This is a Django monorepo.** There is no microservice decomposition, no async task queue (Celery, etc.), and no container orchestration. All logic lives within Django apps inside this single repo.

---

## Repo Structure

Assume a standard Django project layout unless stated otherwise:

```
commands.txt
core
data
docker-compose.yml
manage.py
misc
orthanc.json
postgres.json
prompt.md
radport
requirements.txt
secrets.txt
stocks.md
tree.log
venv

./core:
__init__.py
__pycache__
admin.py
ai
apps.py
integrations
merge_answers_questions.py
migrations
models
pacs
serializers
tests.py
urls.py
utils.py
views.py



./core/ai:
__init__.py

pub_med_classifier.py

./core/integrations:
__init__.py
llm_integrations.py

./core/migrations:
0001_initial.py
0002_studyreport_submitted_by.py
0003_remove_studyreport_unique_submitted_report_per_study_flow_and_more.py
__init__.py



./core/models:
__init__.py
flow.py
study.py



./core/pacs:
__init__.py
pacs_integrations.py
pacs_views.py
urls.py



./core/serializers:
__init__.py
enriched_response.py
flow.py
study.py


./data:
AbdCT.json
CXR.json

./misc:
svs_dicom.py

./radport:
__init__.py
asgi.py
settings.py
urls.py
wsgi.py

```

**If the actual layout differs**, update this tree. This is the canonical reference.

---

## Core Architecture

### 1. Authentication & Users
- JWT-based authentication using Django REST Framework.
- Token retrieval endpoint (login) and token refresh endpoint (refresh).
- User model is Django's built-in `User` or a custom user model — confirm which before making changes.
- No OAuth2, no social login, no multi-factor auth at this stage.

### 2. PACS Proxy (Not DICOM Processing)
- **The backend does NOT process, parse, or store DICOM files.**
- The backend acts as a **proxy** between the frontend and the PACS server.
- It authenticates users internally, then forwards authorized requests to PACS.
- The frontend never calls the PACS server directly — all PACS traffic goes through this backend.
- Treat PACS credentials as sensitive. Never log them. Never hardcode them. Use environment variables.

### 3. Checklist System
- Checklist content is stored in the database.
- Templates are associated with study types (currently: chest X-ray only).
- There is a separate classification component (not in this repo) that determines the study type. This repo receives the classified study type and returns the appropriate checklist template.
- When adding new checklist templates, ensure they map to the correct study type identifier.

### 4. LLM Integration (Anthropic)
- The backend calls the Anthropic API to generate draft reports.
- **Prompt structure is being integrated in the coming days.** Once added, this `CLAUDE.md` must be updated with:
  - Where prompts are stored (DB, settings file, separate module)
  - How checklist findings are injected into prompts
  - Temperature/model parameters
- Until prompt structure is integrated, any LLM-related code should be written with an abstraction layer so prompts can be swapped in later without rewriting business logic.
- **Critical framing rule:** The LLM is a **documentation assistant**, not a diagnostic tool. Any prompt text, API response handling, or UI-facing language must reflect this distinction. The physician is always the decision-maker.

### 5. Report Generation & PDF Export
- Finalized reports are exported as **PDF files** to prevent tampering.
- PDFs are stored on the server filesystem.
- No digital signature integration yet — this is a future feature.
- Report content, once finalized, should be considered immutable in the database.

### 6. Audit Logging
- Currently **basic logging only** — actions are logged but without the full tamper-evident architecture planned for production.
- Log physician actions with timestamp and user attribution.
- When the compliance layer is added later, the audit system will need to be redesigned. Write audit code with the expectation that it will be refactored — keep it isolated in its own app/module.

---

## API Design Rules

- **REST only.** No GraphQL, no gRPC.
- **No API versioning** — there is only one frontend client. If a breaking change is needed, coordinate with the frontend repo (the solo dev owns both).
- Endpoints return JSON. Use DRF serializers for all responses.
- Pagination: use DRF's built-in pagination for list endpoints that could grow.
- Error responses should follow a consistent format. Use DRF's exception handling.
- **All endpoints that touch patient data or PACS must require authentication.** No anonymous access to clinical endpoints.

---

## Database Rules

- PostgreSQL only. No SQLite, even for local development (behavior differences will cause bugs).
- Use Django migrations for all schema changes. Never modify the database schema manually.
- Run `python manage.py makemigrations` after model changes. Commit migration files to the repo.
- **Never commit database credentials.** Use environment variables or a `.env` file (ensure `.env` is in `.gitignore`).

---

## Security Rules (Non-Negotiable)

1. **Secrets never in code.** API keys, database passwords, PACS credentials, JWT signing keys — all from environment variables.
2. **JWT tokens must have reasonable expiry.** Access tokens: short-lived (e.g., 15-60 min). Refresh tokens: longer but with rotation.
3. **PACS credentials flow through the backend only.** The frontend must never receive PACS hostnames, ports, or credentials.
4. **LLM API keys are server-side only.** Never expose them to the frontend.
5. **No debug mode in production.** `DEBUG=False`, proper `ALLOWED_HOSTS`.
6. **Audit log every report generation, every report finalization, every login.** Even if basic, the hooks must be in place.

---

## Development Workflow

### Solo Developer Rules
- **Push directly to `main`.** No branches, no PRs, no code review.
- Keep the repo in a deployable state. If you push broken code, you own the fix.
- Commit messages follow **Conventional Commits**: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`.

### Local Setup
```bash
# Clone the repo
git clone <repo-url>
cd radport-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (example)
export DATABASE_URL=postgres://user:pass@localhost:5432/radport
export ANTHROPIC_API_KEY=sk-...
export PACS_BASE_URL=https://pacs.internal.example.com
export SECRET_KEY=your-django-secret-key

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

### Manual Testing Before Deployment
- There is no automated test suite yet.
- Before deploying, manually run through the core workflow: login → receive checklist → AI draft → edit → finalize → PDF export.
- Check that PACS proxy auth works end-to-end with the actual PACS server.
- Verify JWT token refresh flow works without errors.

### Deployment
- Currently manual. Steps should be documented here once standardized.
- Update this section when deployment process is formalized.

---

## Coding Conventions

| Thing | Convention | Example |
|---|---|---|
| Python files | `snake_case` | `report_service.py` |
| Django models | PascalCase, singular | `ChecklistTemplate`, `AuditLog` |
| Django views | DRF: `ModelViewSet` or `APIView` subclasses | `ChecklistViewSet` |
| Serializers | Model name + `Serializer` | `ReportSerializer` |
| URL endpoints | `kebab-case` | `/api/chest-xray-checklist/` |
| Environment variables | `UPPER_SNAKE_CASE` | `PACS_BASE_URL` |
| Commit messages | Conventional Commits | `feat: add chest X-ray checklist endpoint` |

### Python/Django Rules
- Follow PEP 8.
- Use type hints where practical.
- Keep business logic in model methods or service modules, not in views.
- Views should be thin: validate input, call service/model, serialize response.
- Use DRF serializers for validation — not manual `request.data` parsing.
- Use `select_related()` and `prefetch_related()` for query optimization when fetching related objects.

---

## LLM Integration Rules (Critical)

When writing or editing LLM-related code:

1. **The LLM is a documentation tool, not a diagnostic tool.** This framing must be reflected in:
   - Prompt text sent to Anthropic
   - Response parsing logic
   - Any text stored in the database that could be displayed to users
2. **Never send raw DICOM data or PACS metadata to the LLM.** Only send structured checklist findings.
3. **Temperature and model parameters** should be configurable via settings or environment variables — not hardcoded.
4. **Prompt injection risk:** Checklist findings are user-provided data. Sanitize or structure them before insertion into prompts. Use structured prompt formats (e.g., XML tags, system/user message separation) to prevent prompt injection.
5. **Log LLM requests and responses** for debugging and future audit purposes. Include token usage, latency, and which model was called.

---

## PACS Integration Rules

- The backend is a **proxy**, not a DICOM processor.
- It authenticates the user, then forwards requests to the PACS server.
- PACS credentials (service account or user-delegated) are managed server-side.
- **Never return raw PACS responses directly to the frontend** without sanitization if they contain internal metadata.
- If the PACS server is unreachable, return a clear, user-friendly error — not a raw connection error.

---

## What to Always Do

- ✅ Use environment variables for all secrets and configuration
- ✅ Run migrations before testing schema changes
- ✅ Update `requirements.txt` when adding new packages (`pip freeze > requirements.txt`)
- ✅ Log all report generation and finalization events
- ✅ Validate all input through DRF serializers
- ✅ Keep LLM prompts and API keys server-side only
- ✅ Use `select_related`/`prefetch_related` for query efficiency

## What to Never Do

- ❌ Process or parse DICOM files on the backend
- ❌ Hardcode secrets, keys, or credentials
- ❌ Expose PACS hostnames or internal URLs to the frontend
- ❌ Send raw PACS data or DICOM metadata to the LLM
- ❌ Describe the AI as making diagnoses or clinical decisions
- ❌ Push database migrations without testing them locally
- ❌ Skip audit logging on clinical actions
- ❌ Return HTML error pages from API endpoints — always JSON

---

## Common Tasks & How to Do Them

### Add a New API Endpoint
1. Create or update the serializer in the relevant app's `serializers.py`
2. Add the view (ViewSet or APIView) in `views.py`
3. Register the URL in the app's `urls.py`
4. Include the app URLs in `radport/urls.py` if not already included
5. Test manually with the dev server
6. Update this `CLAUDE.md` if the endpoint is part of a new feature area

### Add a New Model
1. Define the model in `models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Commit the migration file
5. Create serializer and views if the model is API-facing

### Add a New Python Dependency
```bash
pip install package-name
pip freeze > requirements.txt
```
Commit the updated `requirements.txt`.

### Test the LLM Integration
- Ensure `ANTHROPIC_API_KEY` is set in the environment
- Trigger a report draft through the API
- Verify the response is structured correctly
- Check that audit log recorded the LLM call

### Troubleshoot PACS Proxy Issues
- Verify PACS server is reachable from the backend server
- Check that PACS credentials are correct in environment variables
- Ensure the authenticated user has permission to access the requested study
- Log PACS request/response (without sensitive data) for debugging

---

## Questions Before Starting Any Task

Before writing code, you should be able to answer:

1. Does this change touch the database? → Run migrations, commit them
2. Does this expose new data via API? → Add serializer, check auth
3. Does this involve the LLM? → Ensure prompts frame AI as documentation assistant
4. Does this touch PACS? → Proxy only, no DICOM processing, no credential leaks
5. Does this need audit logging? → Log it with user ID and timestamp
6. Is there a new secret or config value? → Environment variable, never hardcoded
7. Does this need a new dependency? → Update `requirements.txt`

---

## Integration Touchpoints with Frontend

The frontend (`radport-frontend`, static site on Cloudflare Pages) communicates exclusively with this backend via REST API. Key integration points to keep aligned:

- **Auth endpoints:** Login returns JWT tokens that the frontend stores and sends as `Authorization: Bearer <token>`
- **Checklist endpoint:** Frontend requests checklist for a study type → backend returns structured checklist
- **Report draft endpoint:** Frontend sends completed checklist → backend calls Anthropic → returns draft text
- **Report finalize endpoint:** Frontend sends final text → backend generates PDF, logs audit event
- **PACS image retrieval:** Frontend requests image → backend proxies to PACS → returns image data

When changing API behavior, **update the frontend accordingly** (or coordinate the change since the same developer owns both repos).

---

*Last updated: May 2026 — keep this file current as the repo grows. Update this file when prompt structure is integrated, when deployment process is formalized, and when new study types are added.*
```
