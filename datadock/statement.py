import logging
import re
from functools import total_ordering

import sqlalchemy as sa

from datadock.helpers import extract_type_annotations, extract_flag_comment, check_flag


@total_ordering
class Statement:
    def __init__(self, filename: str):
        self.filename = filename
        self.name = re.sub("^[0-9][0-9]_", "", re.sub(".sql$", "", filename))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.filename=}, {self.name=})"

    def __str__(self):
        return self.__repr__()

    def __call__(self, default_source_url=None):
        self.run(default_source_url=default_source_url)

    def __gt__(self, other):
        return self.filename > other.filename

    def __eq__(self, other):
        return self.filename == other.filename

    def has_ordering_tag(self):
        return True if re.findall("^[0-9][0-9].*_", self.filename) else False

    def reload(self):
        with open(self.filename, "r") as f:
            self.sql = f.read()

        self.source_url = extract_flag_comment(self.sql, '--source')

    def run(self, default_source_url=None):
        self.reload()

        if not self.source_url:
            if not default_source_url:
                raise RuntimeError("No --source flag found in sql and no default_source_url specified.")
            else:
                self.source_url = default_source_url

        engine = sa.create_engine(self.source_url)

        logging.info(f"Running {self.filename}")
        with engine.connect() as conn:
            result = conn.execute(sa.text(self.sql))
            return result


class StatementReturn:
    def __init__(self, filename: str):
        self.filename = filename
        self.name = re.sub("^[0-9][0-9]_", "", re.sub(".sql$", "", filename))
        self.reload()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.filename=}, {self.name=})"

    def __str__(self):
        return self.__repr__()

    def __call__(self):
        self.run()

    def reload(self):
        with open(self.filename, "r") as f:
            self.sql = f.read()

        self.columns = extract_type_annotations(self.sql)
        self.from_url = extract_flag_comment(self.sql, '--from')
        self.to_url = extract_flag_comment(self.sql, '--to')
        self.name = extract_flag_comment(self.sql, '--name')
        self.return_data = check_flag(self.sql, '--return-data')

        self.table = self.table_from_sql()

    def table_from_sql(self):
        cols = []
        for name, type_string in self.columns.items():
            mylocalenv = {}

            #############################################
            # Be careful, vulnerable to code injection. #
            #############################################
            exec(
                'typ = ' + type_string,
                sa.types.__dict__.copy(),
                mylocalenv
            )

            cols.append(sa.Column(name=name, type_=mylocalenv['typ']))

        meta = sa.MetaData()
        return sa.Table(
            self.name,
            meta,
            *cols
        )

    def get_rows(self):
        engine = sa.create_engine(self.from_url)
        stmt = sa.text(self.sql).columns(*self.table.c)

        with engine.connect() as conn:
            result = conn.execute(stmt)
            return list(result.fetchall())

    def run_basic_sql(self):
        engine = sa.create_engine(self.from_url)

        with engine.connect() as conn:
            result = conn.execute(sa.text(self.sql))
            return result

    def to_sqlite_db(self, rows, clobber=False):
        assert ':///' in self.to_url
        assert len(self.table.metadata.tables) == 1

        rowdicts = [{k: v for k, v in zip(self.table.c, r)} for r in rows]

        engine = sa.create_engine(self.to_url)
        with engine.connect() as conn:
            if clobber:
                i = sa.inspect(conn)
                tablenames = i.get_table_names()
                if self.table.name in tablenames:
                    self.table.drop(conn)

            self.table.metadata.create_all(engine)

            stmt = sa.insert(self.table).values(rowdicts)
            conn.execute(stmt)

    def run(self):
        self.reload()

        if self.return_data:
            rows = self.get_rows()
            self.to_sqlite_db(rows)
        else:
            self.run_basic_sql()
