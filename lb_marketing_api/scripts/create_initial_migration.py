#!/usr/bin/env python3
"""
Helper script to create the initial Alembic migration.
Run this after setting up Alembic to create your first migration.

Usage:
    python scripts/create_initial_migration.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Change to the project root directory
project_root = Path(__file__).parent.parent
os.chdir(project_root)

print("Creating initial Alembic migration...")
print("This will generate a migration file based on your current models.")

try:
    # Create initial migration
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
        check=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print("\n✓ Initial migration created successfully!")
    print("\nNext steps:")
    print("1. Review the migration file in alembic/versions/")
    print("2. Make any necessary adjustments")
    print("3. Run 'alembic upgrade head' to apply the migration")
    
except subprocess.CalledProcessError as e:
    print(f"Error creating migration: {e.stderr}", file=sys.stderr)
    sys.exit(1)
except FileNotFoundError:
    print("Error: Alembic not found. Make sure it's installed:")
    print("  pip install alembic")
    sys.exit(1)

