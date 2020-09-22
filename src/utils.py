import os
import time
from datetime import datetime

import plotille
from alembic.command import upgrade
from alembic.config import Config


def to_unix_timestamp(date: datetime) -> int:
    return int(time.mktime(date.timetuple()))


def from_unix_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp)


def plot_graph(data):
    fig = plotille.Figure()
    fig.color_mode = "byte"
    fig.height = 15
    fig.width = 130
    fig.plot([x[2] for x in data], [x[1] for x in data], lc=42)
    fig.show()
    print(fig.show())


def convert_into_currency(data, exchange):
    if not exchange:
        return
    for item in data:
        item[1] /= exchange


def run_sql_migrations():
    migrations_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "model")
    config = Config(file_=os.path.join(migrations_dir, "alembic.ini"))
    config.set_main_option("script_location", os.path.join(migrations_dir, "stock"))

    # upgrade the database to the latest revision
    upgrade(config, "head")
