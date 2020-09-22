#!/usr/bin/env python

from datetime import datetime

import typer
from tabulate import tabulate

from src import db
from src.api import get_fx_rate_from_usd
from src.utils import convert_into_currency, plot_graph, run_sql_migrations

app = typer.Typer()


@app.command()
def available_stocks():
    typer.echo("Available Stocks:")
    with db.engine.connect() as connection:
        for x in db.get_stock_codes(connection):
            typer.echo(x)


@app.command()
def stock_history(
    code: str, graph: bool = False, currency: str = "", start: datetime = None, end: datetime = None
):
    data = []

    with db.engine.connect() as connection:
        for item in db.get_stock_history(connection, code, start, end):
            data.append([item["code"], item["value"], item["date"]])

    if currency:
        exchange = get_fx_rate_from_usd(currency)
        if not exchange:
            typer.echo(f"Currency {exchange} not found")
        else:
            convert_into_currency(data, exchange)

    if graph:
        plot_graph(data)
    else:
        typer.echo("History:")
        typer.echo(tabulate(data, headers=["code", "value", "date"], tablefmt="presto"))


@app.command()
def stock_info(code: str, exchange: str = ""):
    typer.echo(f"Latest data for {code}:")
    with db.engine.connect() as connection:
        date, value, description = list(db.get_stock_latest_detail(connection, code))[0]
        if exchange:
            exchange_value = db.get_fx_latest_value(connection, exchange)
            if exchange_value:
                value /= exchange_value
            else:
                typer.echo(f"FX {exchange} not found")
        typer.echo(
            tabulate(
                [[date, value, description]],
                headers=["date", "value", "description"],
                tablefmt="presto",
            )
        )


@app.command()
def fx_history(code: str, graph: bool = False, start: datetime = None, end: datetime = None):
    data = []

    with db.engine.connect() as connection:
        for item in db.get_fx_history(connection, code, start, end):
            data.append((item["code"], item["value"], item["date"]))

    if graph:
        plot_graph(data)
    else:
        typer.echo("History:")
        typer.echo(tabulate(data, headers=["code", "value", "date"], tablefmt="presto"))


@app.command()
def init_db(only_data: bool = True):
    if not only_data:
        run_sql_migrations()
    db.fill_db()


if __name__ == "__main__":
    app()
