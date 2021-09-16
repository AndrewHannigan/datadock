import os
from datadock import Statement, Dock
import click


@click.group()
def datadock():
    pass

@datadock.command()
@click.option('--url', default=str, help='Add default sqlalchemy engine url')
@click.argument('filename', required=False)
def run(url, filename):
    if filename:
        stmt = Statement(filename=filename)
        stmt.run()
    else:
        d = Dock(default_source_url=url, directory=os.getcwd())
        d.run_dag()
