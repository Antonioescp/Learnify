"""empty message

Revision ID: b061a96b89a0
Revises: 0e40fc2924c9
Create Date: 2021-12-05 00:26:53.661430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b061a96b89a0'
down_revision = '0e40fc2924c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('audio_fn', sa.String(length=128), nullable=True),
    sa.Column('img_fn', sa.String(length=128), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('options')
    # ### end Alembic commands ###
