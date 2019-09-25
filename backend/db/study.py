from db.table import Table
from pypika.pseudocolumns import PseudoColumn


class Study(Table):
    name = 'studies'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS studies (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER NOT NULL REFERENCES patients(id),
            study_id TEXT NOT NULL,
            description TEXT,
            UNIQUE(patient_id, study_id)
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS studies_study_id ON studies(study_id);
        """)

    async def insert_or_select(self, data):
        q = self.select('*').where(
            self.table.study_id == data['study_id']
        ).where(
            self.table.patient_id == data['patient_db_id']
        )
        s = await self.fetchone(q)
        if s:
            return s

        q = self.insert().columns(
            'patient_id', 'study_id', 'description',
        ).insert((
            data['patient_db_id'], data['study_id'], data['study_description'],
        ), ).on_conflict(
            'patient_id, study_id'
        ).do_update(
            self.table.description, PseudoColumn('EXCLUDED.description'),
        ).returning('id')

        sid = await self.fetchval(q)
        return {'id': sid}
