"""요청별 SQLite 연결과 데이터를 보존하는 초기화 명령."""

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    with current_app.open_resource("schema.sql") as schema:
        get_db().executescript(schema.read().decode("utf-8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """기존 데이터를 지우지 않고 필요한 테이블을 생성합니다."""
    init_db()
    click.echo("데이터베이스가 준비되었습니다. 기존 데이터는 유지됩니다.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
