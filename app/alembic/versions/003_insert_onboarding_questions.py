"""insert onboarding questions

Revision ID: 003_insert_onboarding_questions
Revises: 002_insert_onboarding_questions
Create Date: 2025-09-01 04:45:00
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003_insert_onboarding_questions"
down_revision: Union[str, None] = "002_insert_onboarding_questions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Check if table exists before truncating
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'onboard_quest'
        )
    """))
    if result.scalar():
        conn.execute(sa.text("TRUNCATE onboard_quest RESTART IDENTITY CASCADE"))

        # Insert fresh questions with metadata
        conn.execute(sa.text("""
            INSERT INTO onboard_quest (question_id, title, description, icon)
            VALUES
            (1, 'Hey there 👋 How did you first hear about me?', 'This helps us understand how to better serve our community', 'MessageCircle'),
            (2, 'Great! And which of these best describes you right now?', 'This helps us personalize your experience', 'GraduationCap'),
            (3, 'What''s your current career vibe?', 'Tell us where you''re at in your career journey', 'TrendingUp'),
            (4, 'What field or career path are you most interested in?', 'E.g., Data Analytics, Cloud Engineering, Product Management, Cybersecurity…', 'Target'),
            (5, 'I can adapt to your style. How do you want me to communicate with you?', 'This helps us match our tone to your preferences', 'MessageCircle'),
            (6, 'Right now, what''s your main focus?', 'This helps us tailor your experience', 'Target'),
            (7, 'Where in the world are you? 🌏', 'This helps us provide region-specific insights', 'MapPin'),
            (8, 'If we zoom into just the next 90 days, what''s your #1 objective?', 'What do you want to achieve most?', 'Flag'),
            (9, 'And what feels like your biggest challenge right now?', 'Understanding your challenges helps us provide better support', 'AlertTriangle'),
            (10, 'Want to save me some time? Upload your resume or drop your LinkedIn link (optional).', 'Get more personalized career guidance', 'FileText')
        """))


def downgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'onboard_quest'
        )
    """))
    if result.scalar():
        conn.execute(sa.text("TRUNCATE onboard_quest RESTART IDENTITY CASCADE"))
