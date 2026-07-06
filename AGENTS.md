# 🤖 AI Agent Guidance for Cortex

Welcome, AI Agent! This document provides instructions and context to help you effectively contribute to the Cortex repository.

## 🎯 Coding Principles

1. **Async Perfection**: All I/O operations (DB, Redis, Network) must be `async`. Avoid blocking calls in the `api` package.
2. **Type Safety**: Use Python type hints for all function signatures and variable definitions.
3. **Structured Logging**: Always use `logger` from `api.app.logging` instead of `print()`. Include relevant context in log messages.
4. **Adapter Pattern**: When adding new integrations (e.g., a new CRM or notification service), implement a new adapter in `api.app.adapters` following the existing interfaces.

## 🛠 Project Structure

- `api/app/models/`: Add new database tables here.
- `api/app/services/`: Place complex business logic here, keeping models clean.
- `api/app/schemas/`: Use Pydantic models for data validation and API payloads.
- `api/tests/`: Every new feature must include corresponding unit tests.

## 🧪 Verification Workflow

Before submitting any changes, you **MUST** run the following:

1. **Diagnostics**: `python3 scripts/diagnostics.py`
2. **Tests**: `python3 -m pytest`
3. **Linting**: Run `ruff check .` if available.

## 📝 Common Tasks

- **Adding a Lead Attribute**: Modify `api/app/models/lead.py`, run migrations (if using Alembic), and update `api/app/services/digest.py` if the attribute affects scoring.
- **Adding a Notification Channel**: Create a new class in `api/app/adapters/notifications/` inheriting from `NotificationAdapter`.
