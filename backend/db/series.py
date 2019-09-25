from db.table import Table
from pypika.pseudocolumns import PseudoColumn


class Series(Table):
    name = 'series'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS series (
            id SERIAL PRIMARY KEY,
            study_id INTEGER NOT NULL REFERENCES studies(id),
            number TEXT NOT NULL,
            modality TEXT NOT NULL,
            description TEXT,
            UNIQUE(study_id, number)
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS series_number ON series(number);
        """)

    async def insert_or_select(self, data):
        q = self.select('*').where(
            self.table.study_id == data['study_db_id']
        ).where(
            self.table.number == data['series_number']
        )
        s = await self.fetchone(q)
        if s:
            return s

        q = self.insert().columns(
            'study_id', 'number', 'modality', 'description',
        ).insert((
            data['study_db_id'], data['series_number'], data['modality'], data['series_description'],
        ),).on_conflict(
            'study_id, number'
        ).do_update(
            self.table.number, PseudoColumn('EXCLUDED.number')
        ).returning('id')

        sid = await self.fetchval(q)
        return {'id': sid}
