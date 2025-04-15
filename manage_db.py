#!/usr/bin/env python3
"""
Script to initialize and clean the database.

Usage:
    python manage_db.py                       # To create the database if not already present.
    python manage_db.py --clean               # To drop and recreate all tables.
    python manage_db.py --db_url "sqlite:///custom.db"   # To specify a custom database URL.
"""

import argparse
from sqlalchemy import create_engine
from db_ops.models import Base

def create_db(db_url):
    """Creates the database tables according to the ORM models."""
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    print(f"Database created or already exists at: {db_url}")

def clean_db(db_url):
    """Drops and recreates the database tables."""
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print(f"Database cleaned and re-created at: {db_url}")

def main():
    parser = argparse.ArgumentParser(description="Database Setup and Cleanup")
    parser.add_argument("--clean", action="store_true", help="Clean (drop and recreate) the database.")
    parser.add_argument("--db_url", type=str, default="sqlite:///ble_data.db", help="Database URL")
    args = parser.parse_args()

    if args.clean:
        clean_db(args.db_url)
    else:
        create_db(args.db_url)

if __name__ == "__main__":
    main()
