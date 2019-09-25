from pypika.dialects import PostgreSQLQuery as Query_
from pypika import Table as Table_


class Table:
    tables = []
    name = None

    @staticmethod
    def register(cls):
        Table.tables.append(cls)

    def __init__(self, conn=None, alias=None):
        self.conn = conn
        self.table = Table_(self.name, alias=alias)

    async def sync_db(self):
        raise NotImplemented()

    def query(self):
        return Query_.from_(self.table)

    def select(self, *terms):
        return self.query().select(*terms)

    def update(self):
        return Query_.update(self.table)

    def insert(self):
        return Query_.into(self.table)

    async def fetch(self, q):
        return await self.conn.fetch(str(q))

    async def fetchone(self, q):
        return await self.conn.fetchrow(str(q))

    async def fetchval(self, q):
        return await self.conn.fetchval(str(q))

    async def exec(self, q):
        return await self.conn.execute(str(q))
