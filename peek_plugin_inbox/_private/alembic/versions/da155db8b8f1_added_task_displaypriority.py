"""Added Task.displayPriority

Peek Plugin Database Migration Script

Revision ID: da155db8b8f1
Revises: 297359a078eb
Create Date: 2017-04-16 19:18:25.347113

"""

# revision identifiers, used by Alembic.
revision = "da155db8b8f1"
down_revision = "297359a078eb"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "Task",
        sa.Column("displayPriority", sa.Integer(), server_default="0", nullable=True),
        schema="pl_inbox",
    )
    op.execute('UPDATE "pl_inbox"."Task" set "displayPriority" = 0;')
    op.alter_column(
        "Task", "displayPriority", schema="pl_inbox", nullable=False, type_=sa.Integer()
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("Task", "displayPriority", schema="pl_inbox")
    # ### end Alembic commands ###
