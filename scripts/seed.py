"""
Seed the database from the repository root:

    python scripts/seed.py

Delegates to ``apps/api/app/db/seed.py`` so there is a single source of truth
for seed data. Configure the target database via environment variables or an
``apps/api/.env`` file (see ``.env.example``).
"""

import sys
from pathlib import Path

# Add the api directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ai-sales-qualifier" / "apps" / "api"))

from app.db.seed import main  # noqa: E402  (path setup must precede import)

if __name__ == "__main__":
    main()
