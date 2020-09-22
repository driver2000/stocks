"""create schema

Revision ID: 3c7dd393b9dd
Revises:
Create Date: 2020-09-21 17:02:26.489718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c7dd393b9dd"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create schema stock")
    op.create_table(
        "statics",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("country", sa.String(3), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("exchange", sa.Text(), nullable=False),
        sa.Column("finnhubIndustry", sa.Text(), nullable=False),
        sa.Column("ipo", sa.Date(), nullable=False),
        schema="stock",
    )

    op.create_table(
        "quote",
        sa.Column(
            "code",
            sa.Text(),
            sa.ForeignKey("stock.statics.code", onupdate="cascade", ondelete="cascade"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("code", "date"),
        schema="stock",
    )

    op.execute("create schema fx")
    op.create_table(
        "rate",
        sa.Column("code", sa.Text(), primary_key=True),
        sa.Column("description", sa.Unicode(), nullable=False),
        sa.Column("external_code", sa.Unicode(), nullable=False),
        schema="fx",
    )
    op.create_table(
        "quote",
        sa.Column(
            "code",
            sa.Text(),
            sa.ForeignKey("fx.rate.code", onupdate="cascade", ondelete="cascade"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("code", "date"),
        schema="fx",
    )


def downgrade():
    op.drop_table("quote", schema="stock")
    op.drop_table("statics", schema="stock")
    op.drop_table("quote", schema="fx")
    op.drop_table("rate", schema="fx")
    op.execute("drop schema stock cascade")
    op.execute("drop schema fx cascade")
