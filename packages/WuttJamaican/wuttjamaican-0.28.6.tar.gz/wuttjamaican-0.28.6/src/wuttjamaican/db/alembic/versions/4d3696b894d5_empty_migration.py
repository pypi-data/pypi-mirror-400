"""empty migration

Revision ID: 4d3696b894d5
Revises: b59a34266288
Create Date: 2025-12-28 13:56:20.900043

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import wuttjamaican.db.util


# revision identifiers, used by Alembic.
revision: str = "4d3696b894d5"
down_revision: Union[str, None] = "b59a34266288"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# NOTE: this empty revision exists simply to ensure that its down
# revision (b59a34266288) is not the branch head.  and that is needed
# because some of the tests in wuttaweb now run commands like these:
#
#     alembic downgrade wutta@-1
#     alembic upgrade heads
#
# which is actually fine for postgres but not so for sqlite, due to
# the particular contents of the b59a34266288 revision.


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
