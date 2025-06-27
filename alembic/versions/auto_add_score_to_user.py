"""add score column to users

Revision ID: add_score_to_user
Revises: 14ffc65a3664
Create Date: 2025-06-26
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_score_to_user'
down_revision = '14ffc65a3664'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('score', sa.Integer(), server_default='0'))

def downgrade():
    op.drop_column('users', 'score') 