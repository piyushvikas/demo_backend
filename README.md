# demo-backend

A small FastAPI backend (users, products, orders, in-memory storage) built
specifically to exercise the [ops-factory](https://github.com/piyushvikas/demo_cli_agent)
CI/CD pipeline: a pytest TDD gate + Forge AI PR review, running together on
every pull request.

This is a demo/test fixture, not a real product — logic is intentionally
simple (no real database, no production-grade auth) so the focus stays on
the pipeline, not the app. Fcker

## Structure

```
main.py                # FastAPI routes
app/
  models.py            # Pydantic request/response schemas
  storage.py           # in-memory repositories
  services/
    auth.py            # password hashing, tokens
    users.py            # user CRUD + authentication
    products.py          # product CRUD + stock management
    orders.py            # order creation, pricing, cancellation
  utils/
    validators.py       # email/phone/username/password validation
    pricing.py           # tax, discount, shipping calculations
tests/                  # 100+ test cases across unit + API layers
```

## Running locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload   # http://localhost:8000/docs
```

## Running tests

```bash
pytest -v
```

## CI

`.github/workflows/ci.yml` runs on every PR:
1. **`test`** — the actual pytest suite. This is the real TDD enforcement gate.
2. **`forge-review`** — calls ops-factory's reusable Forge review workflow for AI code review.

Set these repo secrets before opening a PR:
- `OPENAI_API_KEY`
- `FORGE_PAT` (optional — falls back to `GITHUB_TOKEN`)

To actually enforce the gate, add branch protection on `main` requiring both
the `test` status check and a PR approval (see ops-factory's docs for why
approvals — not just status checks — are what make Forge's `REQUEST_CHANGES`
block a merge).

> **Note:** the `forge-review` job pins `@v0` (ops-factory's floating
> pre-1.0 tag). If that tag doesn't exist yet in your ops-factory repo,
> pin to whatever tag `auto-release.yml` actually created there instead.

