"""change tg_id to BigInteger

Revision ID: change_tg_id_to_bigint
Revises: 5a6ddca80ef3
Create Date: 2025-06-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'change_tg_id_to_bigint'
down_revision = '5a6ddca80ef3'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('tg_id',
            existing_type=sa.Integer(),
            type_=sa.BigInteger(),
            existing_nullable=False)

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('users', 'tg_id',
            existing_type=sa.BigInteger(),
            type_=sa.Integer(),
            existing_nullable=False) 