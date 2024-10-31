"""empty message

Revision ID: 31cad41a2d24
Revises: dd2368972cc7
Create Date: 2024-07-28 15:03:38.346803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31cad41a2d24'
down_revision = 'dd2368972cc7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exercises',
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('workout_id', sa.Integer(), nullable=True),
    sa.Column('exercise_name', sa.String(length=50), nullable=True),
    sa.Column('number_of_sets', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['workout_id'], ['workout.workout_id'], ),
    sa.PrimaryKeyConstraint('exercise_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('exercises')
    # ### end Alembic commands ###
