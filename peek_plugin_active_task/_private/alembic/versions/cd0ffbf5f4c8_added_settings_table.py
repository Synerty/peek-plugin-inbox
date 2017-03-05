"""Added settings table

Peek Plugin Database Migration Script

Revision ID: cd0ffbf5f4c8
Revises: b46842ff393c
Create Date: 2017-03-05 23:19:00.059284

"""

# revision identifiers, used by Alembic.
revision = 'cd0ffbf5f4c8'
down_revision = 'b46842ff393c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Setting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='pl_active_task'
    )
    op.create_table('SettingProperty',
    sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
    sa.Column('settingId', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('type', sa.String(length=16), nullable=True),
    sa.Column('int_value', sa.Integer(), nullable=True),
    sa.Column('char_value', sa.String(), nullable=True),
    sa.Column('boolean_value', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['settingId'], ['pl_active_task.Setting.id'], ),
    sa.PrimaryKeyConstraint('id', 'settingId'),
    schema='pl_active_task'
    )
    op.create_index('idx_SettingProperty_settingId', 'SettingProperty', ['settingId'], unique=False, schema='pl_active_task')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_SettingProperty_settingId', table_name='SettingProperty', schema='pl_active_task')
    op.drop_table('SettingProperty', schema='pl_active_task')
    op.drop_table('Setting', schema='pl_active_task')
    # ### end Alembic commands ###
