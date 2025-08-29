"""insert onboarding questions

Revision ID: 002_insert_onboarding_questions
Revises: 001_onboarding_tables
Create Date: 2025-08-28 10:00:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_insert_onboarding_questions'
down_revision: Union[str, None] = 'a7300fc42c26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   # Clear old data and reset identity sequence
    op.execute("TRUNCATE onboard_quest RESTART IDENTITY CASCADE")

    # Insert fresh questions
    op.execute("""
        INSERT INTO onboard_quest (question)
        VALUES
        ('How did you discover AI Mentor?'),
        ('Which of These Best Describes You?'),
        ('What''s your primary career path?'),
        ('What''s your communication style?'),
        ('What''s your main area of Career focus right now?'),
        ('Where are you located?'),
        ('What''s your primary objective for the next 90 days?')
    """)
    

def downgrade() -> None:
    # Just wipe the questions if rolled back
    op.execute("TRUNCATE onboard_quest RESTART IDENTITY CASCADE")