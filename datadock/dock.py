import sqlalchemy as sa

from datadock.helpers import extract_type_annotations, extract_flag_comment


class Dock:
    def __init__(self, sql: str):
        self.sql = sql

        self.columns = extract_type_annotations(self.sql)
        self.from_url = extract_flag_comment(self.sql, '--from')
        self.to_url = extract_flag_comment(self.sql, '--to')
        self.name = extract_flag_comment(self.sql, '--name')

        self.table = self.extract_sa_table()

    def __repr__(self):
        return self.__class__.__name__ + '\n' + str(self.__dict__)

    def extract_sa_table(self):
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

    def to_sqlite_db(self, rows, clobber=False):
        assert ':///' in self.to_url
        assert len(self.table.metadata.tables) == 1

        rowdicts = [{k: v for k,v in zip(self.table.c, r)} for r in rows]

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
        rows = self.get_rows()
        self.to_sqlite_db(rows)


if __name__ == '__main__':
    test_sql = """
        --from sqlite:////Users/andrewhannigan/PycharmProjects/datadock/tests/tigerking.db
        --to   sqlite:////Users/andrewhannigan/PycharmProjects/datadock/tests/tigerking_new.db
        --name trainer
        SELECT
          first_name                   --type String(length=100)
        , last_name as alias           --type String(length=100)
        , dob                          --type Date
        , CASE WHEN tiger_skills > 0.8
               THEN 1              
               ELSE 0
               END as binary_tiger_skills    --type Integer
        FROM Trainer
        """

    d = Dock(test_sql)
    d.run()
