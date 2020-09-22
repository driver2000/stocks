from datetime import datetime

import typer

from src import db
from src.utils import run_sql_migrations, plot_graph

app = typer.Typer()


@app.command()
def available_stocks():
    typer.echo("Available Stocks:")
    with db.engine.connect() as connection:
        for x in db.get_stock_codes(connection):
            typer.echo(x)


@app.command()
def stock_history(code: str, graph: bool = False, start: datetime = None, end: datetime = None):
    data = []

    with db.engine.connect() as connection:
        for item in db.get_stock_history(connection, code, start, end):
            data.append((item["code"], item["value"], item["date"]))

    if graph:
        plot_graph(data)
    else:
        typer.echo("Available Stocks:")
        for code, value, date in data:
            typer.echo(f"{code} |\t {value} |\t {date}")


@app.command()
def get_stock_info(code: str, exchange: str = ""):
    typer.echo(f"Latest data for {code}:")
    with db.engine.connect() as connection:
        date, value, description = list(db.get_stock_latest_detail(connection, code))[0]
        if exchange:
            exchange_value = db.get_fx_latest_value(connection, exchange)
            if exchange_value:
                value = value / exchange_value
            else:
                typer.echo(f"FX {exchange} not found")
        typer.echo(" | ".join(map(str, [date, value, description])))


@app.command()
def init_db(only_data: bool = True):
    if not only_data:
        run_sql_migrations()
    db.fill_db()


if __name__ == "__main__":
    app()
