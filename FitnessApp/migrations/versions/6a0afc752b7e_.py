"""empty message

Revision ID: 6a0afc752b7e
Revises: 1f4356476b46
Create Date: 2024-07-23 15:32:22.370170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a0afc752b7e'
down_revision = '1f4356476b46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Type of Exercise', sa.String(length=100), nullable=True))
        batch_op.alter_column('Sets',
               existing_type=sa.INTEGER(),
               type_=sa.JSON(),
               existing_nullable=True)
        batch_op.drop_column('Reps')
        batch_op.drop_column('Weight')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workout', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Weight', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('Reps', sa.INTEGER(), nullable=True))
        batch_op.alter_column('Sets',
               existing_type=sa.JSON(),
               type_=sa.INTEGER(),
               existing_nullable=True)
        batch_op.drop_column('Type of Exercise')

    # ### end Alembic commands ###
