from db.table import Table
from pypika import Order
from db.users import Users


class FileChange(Table):
    name = 'file_changes'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS file_changes (
            id SERIAL PRIMARY KEY,
            file_id INTEGER NOT NULL REFERENCES files(id),
            created TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            by_user_id INTEGER NOT NULL REFERENCES users(id),
            type TEXT NOT NULL,
            old TEXT,
            new TEXT
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS file_changes_file_id ON file_changes(file_id);
        """)

    @staticmethod
    def to_json(data):
        data = dict(data)
        return data

    async def add_change(self, file_id, type_, by_user=None, old=None, new=None):
        q = self.insert().columns(
            'file_id', 'type', 'by_user_id', 'old', 'new',
        ).insert(
            file_id, type_, by_user, old, new,
        )
        await self.exec(q)

    async def for_file(self, file_id):
        users = Users()
        q = self.select(self.table.star, users.table.username)\
            .join(users.table).on(users.table.id == self.table.by_user_id)\
            .where(self.table.file_id == file_id)\
            .orderby('id', order=Order.desc)

        data = await self.fetch(q)
        return [self.to_json(d) for d in data]
