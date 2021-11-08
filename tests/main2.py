from datadock import Dock
import logging

logging.basicConfig(level=logging.INFO)
dock = Dock(default_source_url="sqlite:////workspaces/datadock/tests/tigerking.db")
print(dock.another_test_script())
print(dock.test_script())
