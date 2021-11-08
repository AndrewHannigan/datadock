import os
from datadock import Statement, Dock
import click


@click.group()
def datadock():
    pass

@datadock.command()
@click.option('--url', default=str, help='Add default sqlalchemy engine url')
@click.argument('filename', required=True)
def run(url, filename):
    stmt = Statement(filename=filename)
    rows = stmt.run()
    if rows:
        print(rows)
