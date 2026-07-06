# Contributing to AI Sales Lead Qualifier

Thank you for your interest in contributing to the AI Sales Lead Qualifier! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

### Setting Up Your Development Environment

1. **Fork the repository** and clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-sales-qualifier.git
   cd ai-sales-qualifier
   ```

2. **Set up the backend**:
   ```bash
   cd apps/api
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set up the frontend**:
   ```bash
   cd apps/web
   npm install
   ```

4. **Start Docker services**:
   ```bash
   docker compose up -d
   ```

5. **Run migrations**:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

## 📋 Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints everywhere, add docstrings to public functions
- **TypeScript**: Use strict mode, prefer interfaces for object shapes
- **Commits**: Follow Conventional Commits specification

### Running Tests
```bash
# Backend tests
cd apps/api
pytest

# Frontend tests
cd apps/web
npm test
```

### Database Migrations
When modifying models:
```bash
cd apps/api
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## 🔀 Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. Make your changes and ensure tests pass

3. Commit your changes with a descriptive message:
   ```bash
   git commit -m "feat: add new feature description"
   ```

4. Push to your fork and open a Pull Request

5. Fill out the PR template completely

6. Wait for review and address feedback

## 📝 Issue Reporting

Before creating an issue:
1. Check existing issues to avoid duplicates
2. Use the appropriate issue template
3. Provide clear reproduction steps
4. Include environment details (OS, Python version, etc.)

## 🧪 Testing Requirements

All PRs must:
- Include tests for new functionality
- Maintain or improve code coverage
- Pass all existing tests

## 🔒 Security

- Never commit secrets or API keys
- Use `.env.example` as a template for environment variables
- Report security vulnerabilities privately via GitHub Security Advisories

## 💬 Questions?

Open a discussion on GitHub for questions, ideas, or general conversation.

---

By contributing, you agree that your contributions will be licensed under the MIT License.
