import logging
import os
import re
import jinja2
from functools import total_ordering

import sqlalchemy as sa

from datadock.helpers import extract_type_annotations, extract_flag_comment, check_flag

logger = logging.getLogger(__name__)


@total_ordering
class Statement:
    def __init__(self, path: str, default_source_url: str = None, scalarize = False):
        self.path = path
        self.filename = os.path.basename(self.path)
        self.name = re.sub("^[0-9][0-9]_", "", re.sub(".sql$", "", self.filename))
        self.default_source_url = default_source_url
        self.scalarize = scalarize

        # Populated at runtime when run() is called
        self.sql = None
        self.source_url = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.path=}, {self.filename=}, {self.name=})"

    def __str__(self):
        return self.__repr__()

    def __call__(self, **kwargs):
        return self.run(**kwargs)
        
    def __gt__(self, other):
        return self.filename > other.filename

    def __eq__(self, other):
        return self.filename == other.filename

    def has_ordering_tag(self):
        return True if re.findall("^[0-9][0-9].*_", self.filename) else False

    def load(self, **kwargs):
        with open(self.path, "r") as f:
            template = f.read()

        self.sql = jinja2.Template(template).render(kwargs)
        self.source_url = extract_flag_comment(self.sql, '--source')

    def run(self, dry=False, **kwargs):
        self.load(**kwargs)
        
        if dry:
            print(self.sql)
            return
        
        if not self.source_url and not self.default_source_url:
            raise RuntimeError("No --source flag found in sql and no default_source_url specified.")

        engine = sa.create_engine(self.source_url or self.default_source_url)

        logger.info(f"Running {self.filename}")
        with engine.connect() as conn:
            result = conn.execute(sa.text(self.sql))
            rows = result.fetchall()
        
        if rows and self.scalarize and len(rows[0]) == 1:
            rows = [r[0] for r in rows]

        return rows


#TODO
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

