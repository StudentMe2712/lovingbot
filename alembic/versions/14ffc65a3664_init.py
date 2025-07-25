"""init

Revision ID: 14ffc65a3664
Revises: 
Create Date: 2025-06-26 10:24:02.371516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14ffc65a3664'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quiz_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('partner_id', sa.Integer(), nullable=True),
    sa.Column('partner_confirmed', sa.Boolean(), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('quiz_questions')
    # ### end Alembic commands ###
