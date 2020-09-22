from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()


class StockStatics(Base):
    __tablename__ = "statics"
    __table_args__ = {"schema": "stock"}
    code = sa.Column(sa.Text(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False)
    country = sa.Column(sa.String(3), nullable=False)
    currency = sa.Column(sa.String(3), nullable=False)
    exchange = sa.Column(sa.Text(), nullable=False)
    finnhubIndustry = sa.Column(sa.Text(), nullable=False)
    ipo = sa.Column(sa.Date(), nullable=False)


class StockQuote(Base):
    __tablename__ = "quote"
    __table_args__ = (sa.PrimaryKeyConstraint("code", "date"), {"schema": "stock"})
    code = sa.Column(
        sa.Text(),
        sa.ForeignKey(StockStatics.code, onupdate="cascade", ondelete="cascade"),
        nullable=False,
    )
    date = sa.Column(sa.Date(), nullable=False)
    value = sa.Column(sa.Float(), nullable=False)


class FXRate(Base):
    __tablename__ = "rate"
    __table_args__ = {"schema": "fx"}
    code = sa.Column(sa.Text(), primary_key=True)
    external_code = sa.Column(sa.Unicode(), nullable=False)
    description = sa.Column(sa.Unicode(), nullable=False)


class FXQuote(Base):
    __tablename__ = "quote"
    __table_args__ = (sa.PrimaryKeyConstraint("code", "date"), {"schema": "fx"})
    code = sa.Column(
        sa.Text(),
        sa.ForeignKey(FXRate.code, onupdate="cascade", ondelete="cascade"),
        nullable=False,
    )
    date = sa.Column(sa.Date(), nullable=False)
    value = sa.Column(sa.Float(), nullable=False)
