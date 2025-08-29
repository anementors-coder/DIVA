# Import all the models, so that Base has them before being
# imported by Alembic
from sqlalchemy.orm import declarative_base

Base = declarative_base()


