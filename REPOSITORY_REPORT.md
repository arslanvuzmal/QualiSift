# Repository Report: Cortex

## Project Overview
**Cortex** is an **AI Sales Lead Qualifier** platform designed to automate the process of qualifying sales leads. It leverages AI to score leads and provides automated distribution of lead digests through various channels.

## Key Features (based on recent development)
- **Lead Scoring**: Automated qualification of sales leads.
- **Daily Digest Generation**: Compiles Hot, Warm, and Cold lead segments into a daily summary.
- **Multi-channel Notifications**: Supports notifications via Email (SMTP, SendGrid), Slack (Block Kit), and Console.
- **Vector Search Capability**: Infrastructure includes `pgvector` for potential similarity-based lead matching or RAG (Retrieval-Augmented Generation) features.

## Technical Stack
- **Language**: Python
- **Database**: PostgreSQL with `pgvector` (for vector operations)
- **Caching/Messaging**: Redis
- **Infrastructure**: Docker Compose
- **Backend Libraries**: SQLAlchemy (Async), Jinja2 (Templates)

## Repository Structure
- `ai-sales-qualifier/`: A git submodule containing the core application logic (likely the `api` service).
- `scripts/`: Contains maintenance and setup scripts.
  - `seed.py`: Initializes the database schema and prepares it for dummy data.
- `docker-compose.yml`: Defines the local development environment (Postgres & Redis).
- `README.md`: Project entry point (currently minimal).
- `LICENSE`: MIT License.

## Current Status
The repository is in the early stages of integration. The core application logic is linked via a git submodule (`ai-sales-qualifier`), and the infrastructure is ready to be spun up via Docker. The `seed.py` script indicates a two-phase initialization process, with Phase 1 (schema creation) currently implemented.

## Recommendations
1. **Initialize Submodules**: To work with the core logic, ensure submodules are initialized: `git submodule update --init --recursive`.
2. **Expand Documentation**: The `README.md` should be updated with setup instructions and project goals.
3. **Environment Configuration**: A `.env.example` file would be beneficial for managing database URLs and API keys for SendGrid/Slack.
