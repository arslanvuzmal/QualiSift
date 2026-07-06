# Cortex - AI Sales Lead Qualifier

Cortex is an AI-driven platform for qualifying sales leads, scoring them, and distributing digests through multiple notification channels.

## Project Overview
The platform automates the qualification process, enabling sales teams to focus on the highest-value opportunities. It uses AI to categorize leads into Hot, Warm, and Cold segments.

## Infrastructure
- **PostgreSQL (pgvector)**: Core database with vector search capabilities.
- **Redis**: For caching and messaging.
- **Docker Compose**: Orchestrates the development environment.

## Repository Structure
- `ai-sales-qualifier/`: Core application logic (linked as a git submodule).
- `scripts/`: Maintenance and utility scripts.
  - `seed.py`: Database schema initialization.
- `docker-compose.yml`: Infrastructure definition.

## Getting Started
1. Initialize submodules:
   ```bash
   git submodule update --init --recursive
   ```
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. Initialize the database:
   ```bash
   python scripts/seed.py
   ```

For more details, see the [Repository Report](REPOSITORY_REPORT.md).
