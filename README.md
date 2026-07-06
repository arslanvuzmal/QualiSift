# Cortex: Enterprise AI Sales Lead Qualifier

Cortex is a production-grade AI system designed to automate the qualification and segmentation of sales leads. It leverages vector similarity (via pgvector) and intelligent scoring to ensure that sales teams focus on the highest-value opportunities.

## 🚀 Quick Start

### 1. Environment Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file and adjust as needed:
```bash
cp .env.example .env
```

### 3. Initialize Database
Run the seed script to create tables and add dummy data:
```bash
python3 scripts/seed.py
```

### 4. Run Diagnostics
Verify your environment is correctly configured:
```bash
python3 scripts/diagnostics.py
```

## 🏗 Architecture

- **api/app/models**: Database schemas using SQLAlchemy 2.0.
- **api/app/services**: Core business logic (e.g., Digest generation).
- **api/app/adapters**: Pluggable notification channels (Console, Slack, Email).
- **scripts**: Administrative and diagnostic tools.

## 🧪 Testing

Run the test suite using pytest:
```bash
python3 -m pytest
```

## 🛡 Enterprise Features
- **Structured Logging**: All services use centralized logging for observability.
- **Pluggable Adapters**: Easily switch between notification providers without changing business logic.
- **Async First**: Built on Python's `asyncio` for high-concurrency performance.
- **Robust Error Handling**: Integrated try-except blocks with detailed error reporting.

## 🤝 Contributing
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
