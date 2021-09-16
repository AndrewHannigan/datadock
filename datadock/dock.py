import os
import re
import inspect
import logging

from datadock import Statement


class Dock:
    def __init__(self, default_source_url=None, directory=None):
        self.default_source_url = default_source_url
        self.directory = directory or os.path.dirname(inspect.stack()[1].filename)

        self.statements = None

        logging.info(f"Identified directory of Dock() object as: {self.directory}.")

        self.reload()

    def reload(self):
        self.statements = [Statement(f) for f in os.listdir(self.directory) if re.match(".*[.]sql$", f)]

    def run_dag(self):
        dag_statements = [s for s in self.statements if s.has_ordering_tag()]
        dag_statements.sort()

        for s in dag_statements:
            s(default_source_url=self.default_source_url)

    def __getattr__(self, name):
        self.reload()

        for s in self.statements:
            if s.name == name:
                return s

        return super().__getattribute__(name)

