from datetime import datetime

from dateutil.relativedelta import relativedelta

from db.table import Table
from utils import rand_str


class SharedFiles(Table):
    name = 'shared_files'

    async def sync_db(self):
        await self.exec("""    
        CREATE TABLE IF NOT EXISTS shared_files (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            expires TIMESTAMP NOT NULL,
            file_id INTEGER NOT NULL REFERENCES files(id) ON DELETE CASCADE,
            hash TEXT NOT NULL
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS shared_files_hash ON shared_files(hash);
        """)

    async def share(self, file_id, duration):
        key = rand_str()
        expires = datetime.utcnow() + relativedelta(hours=duration)
        q = self.insert().columns(
            'file_id', 'hash', 'expires'
        ).insert(
            file_id, key, expires,
        )
        await self.exec(q)
        return key

    async def check(self, key):
        q = self.select('*').where(self.table.hash == key)
        sf = await self.fetchone(q)
        now = datetime.utcnow()
        if not sf:
            return None

        if sf['expires'] < now:
            q = self.query().where(self.table.id == sf['id']).delete()
            await self.exec(q)
            return None
        return sf['file_id']
