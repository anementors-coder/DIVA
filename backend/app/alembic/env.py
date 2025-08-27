import os
import sys
from logging.config import fileConfig
from pathlib import Path
from sqlalchemy import create_engine

from alembic import context
from sqlalchemy import  pool

# --- START OF OUR CUSTOM CODE ---
# Add the project root to the system path to allow imports like 'from app.core...'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, str(PROJECT_ROOT))

# Import your settings and the Base for your models
from app.core.config import settings
from app.db.base import Base 

# Set the DATABASE_URL environment variable so that alembic.ini can read it
print(">>> settings.DATABASE_URL =", settings.DATABASE_URL)

os.environ['DATABASE_URL'] = str(settings.DATABASE_URL)
# --- END OF OUR CUSTOM CODE ---


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- START OF OUR CUSTOM CODE (MODIFICATION) ---
# Tell Alembic what SQLAlchemy models to look at
target_metadata = Base.metadata
# --- END OF OUR CUSTOM CODE (MODIFICATION) ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.'"""
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()