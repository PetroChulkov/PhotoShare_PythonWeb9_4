"""7

Revision ID: 756195200d06
Revises: 99b184373c3d
Create Date: 2023-05-15 20:02:19.453983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '756195200d06'
down_revision = '99b184373c3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('banned', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'banned')
    # ### end Alembic commands ###
