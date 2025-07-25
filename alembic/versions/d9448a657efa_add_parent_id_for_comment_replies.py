"""add parent_id for comment replies

Revision ID: d9448a657efa
Revises: 9d825d0f71d1
Create Date: 2025-07-12 13:00:17.605115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9448a657efa'
down_revision: Union[str, Sequence[str], None] = '9d825d0f71d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'comments', 'comments', ['parent_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'parent_id')
    # ### end Alembic commands ###
