from datadock import Dock
import logging

logging.basicConfig(level=logging.INFO)
dock = Dock(scalarize=True)
print(dock.some_query())
