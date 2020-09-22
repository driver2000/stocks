import sqlalchemy as sa

from src import api, tables

from .resources import DB_DNS
from .utils import from_unix_timestamp

engine = sa.create_engine(DB_DNS)


def get_stock_codes(connection):
    return (x[0] for x in connection.execute(sa.select([tables.StockStatics.code])))


def get_fx_mapping(connection) -> dict:
    return {
        x[0]: x[1]
        for x in connection.execute(sa.select([tables.FXRate.external_code, tables.FXRate.code]))
    }


def fill_db():
    with engine.begin() as connection:
        print(f"Loading {tables.StockStatics.__table__}")
        connection.execute(
            sa.insert(tables.StockStatics),
            [
                {
                    "code": code,
                    "name": x["name"],
                    "country": x["country"],
                    "currency": x["currency"],
                    "exchange": x["exchange"],
                    "finnhubIndustry": x["finnhubIndustry"],
                    "ipo": x["ipo"],
                }
                for code, x in api.get_stock_statics()
            ],
        )

        print(f"Loading {tables.StockQuote.__table__}")
        for code, data in api.get_stock_histories(get_stock_codes(connection)):
            connection.execute(
                sa.insert(tables.StockQuote),
                [
                    {
                        "code": code,
                        "date": from_unix_timestamp(_date).date(),
                        "value": value,
                    }
                    for value, _date in data
                ],
            )
        print(f"Loading {tables.FXRate.__table__}")
        connection.execute(
            sa.insert(tables.FXRate),
            [
                {
                    "code": x["displaySymbol"],
                    "description": x["description"],
                    "external_code": x["symbol"],
                }
                for x in api.get_fx_rates()
            ],
        )

        print(f"Loading {tables.FXQuote.__table__}")
        fx_mapping = get_fx_mapping(connection)
        for code, data in api.get_fx_histories(fx_mapping.keys()):
            connection.execute(
                sa.insert(tables.FXQuote),
                [
                    {
                        "code": fx_mapping[code],
                        "date": from_unix_timestamp(_date).date(),
                        "value": value,
                    }
                    for value, _date in data
                ],
            )


def get_stock_latest_detail(connection, code):
    latest = (
        sa.select([tables.StockQuote])
        .where(tables.StockQuote.code == code)
        .order_by(sa.desc(tables.StockQuote.date))
        .limit(1)
        .cte("latest")
    )
    return connection.execute(
        latest.join(tables.StockStatics, tables.StockStatics.code == latest.c.code)
        .select()
        .with_only_columns([latest.c.date, latest.c.value, tables.StockStatics.exchange])
    )


def get_fx_latest_value(connection, code):
    return connection.execute(
        sa.select([tables.FXQuote.value])
        .where(tables.FXQuote.code == f"{code}/USD")
        .order_by(sa.desc(tables.FXQuote.date))
        .limit(1)
    ).scalar()


def get_stock_history(connection, code, start=None, end=None):
    qry = (
        sa.select([tables.StockQuote])
        .where(tables.StockQuote.code == code)
        .order_by(sa.desc(tables.StockQuote.date))
    )

    if start:
        qry = qry.where(tables.StockQuote.date >= start)

    if end:
        qry = qry.where(tables.StockQuote.date <= end)

    return connection.execute(qry)
