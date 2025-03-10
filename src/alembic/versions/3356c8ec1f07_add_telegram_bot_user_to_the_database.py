"""add TELEGRAM_BOT user to the database

Revision ID: 3356c8ec1f07
Revises: e9c898561f90
Create Date: 2025-03-09 09:48:34.972608

"""

import os
from typing import Sequence, Union

from alembic import op

from config import load_environ

from database.models import User

from sqlalchemy.sql import table, column
from sqlalchemy import Integer, String


# revision identifiers, used by Alembic.
revision: str = "3356c8ec1f07"
down_revision: Union[str, None] = "e9c898561f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_table_name = User.__tablename__
BOT_ID = 1


def upgrade() -> None:
    load_environ()

    user_table = table(
        user_table_name,
        column("id", Integer),
        column("username", String),
        column("password", String),
    )
    op.bulk_insert(
        user_table,
        [
            {
                "id": BOT_ID,
                "password": User.hash_password(os.getenv("API_BOT_PASSWORD")),
                "username": os.getenv(
                    "API_BOT_USERNAME", default="TELEGRAM_BOT"
                ),
            }
        ],
    )
    op.execute(
        f"SELECT setval('{user_table_name}_id_seq', "
        f"(SELECT MAX(id) FROM public.{user_table_name}));"
    )


def downgrade() -> None:
    op.execute(f"DELETE * FROM public.{user_table_name} WHERE id = {BOT_ID}")
