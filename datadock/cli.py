import sys
from datadock import Dock


def main():
    if len(sys.argv) != 2:
        raise ValueError("Path to SQL file must be provided to datadock")

    with open(sys.argv[1], 'r') as f:
        sql = f.read()
        dock = Dock(sql)
        dock.run()
