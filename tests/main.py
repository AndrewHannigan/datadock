from datadock import Dock
import logging

logging.basicConfig(level=logging.INFO)
dock = Dock(default_source_url="sqlite:////opt/project/tests/tigerking.db")
dock.run_dag()
