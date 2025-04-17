"""Custom migration for enum change

Revision ID: 9c1a04ba27eb
Revises: af35777029cf
Create Date: 2025-04-05 20:28:09.364777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c1a04ba27eb'
down_revision = 'af35777029cf'
branch_labels = None
depends_on = None


def upgrade():
    # Rename enum value "Pending" to "In Queue"
    op.execute("ALTER TYPE queue_status_enum RENAME VALUE 'Pending' TO 'In Queue';")

def downgrade():
    # Revert the change by renaming "In Queue" back to "Pending"
    op.execute("ALTER TYPE queue_status_enum RENAME VALUE 'In Queue' TO 'Pending';")