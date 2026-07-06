"""Container / CLI entrypoint for seeding.

Run from the API package root (this is what the Docker command uses):

    python -m scripts.seed
"""

from app.db.seed import main

if __name__ == "__main__":
    main()
