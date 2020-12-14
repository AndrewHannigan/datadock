import sys
from datadock import Dock


def main():
    with open(sys.argv[1], 'r') as f:
        sql = f.read()
        dock = Dock(sql)
        dock.run()
