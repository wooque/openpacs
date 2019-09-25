from db.table import Table
from db.study import Study
from db.series import Series
from pypika.pseudocolumns import PseudoColumn


class Patient(Table):
    name = 'patients'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            birth_date TEXT,
            sex TEXT,
            meta JSONB
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS patients_patient_id ON patients(patient_id);
        """)

    async def insert_or_select(self, data):
        q = self.select('*').where(self.table.patient_id == data['patient_id'])
        p = await self.fetchone(q)
        if p:
            return p

        q = self.insert().columns(
            'patient_id', 'name', 'birth_date', 'sex',
        ).insert((
            data['patient_id'], data['patient_name'],
            data['patient_birth_date'], data['patient_sex'],
        ),).on_conflict('patient_id').do_update(
            self.table.name, PseudoColumn('EXCLUDED.name'),
        ).returning('id')

        patient_id = await self.fetchval(q)
        return {'id': patient_id}

    async def get_extra(self, patient_id):
        from db.files import Files

        q = self.select('*').where(self.table.id == patient_id)
        patient = await self.fetchone(q)
        patient = dict(patient)

        StudyT = Study(self.conn)
        q = StudyT.select('*').where(
            StudyT.table.patient_id == patient_id
        )
        studies_data = await self.fetch(q)
        studies_data = [dict(s) for s in studies_data]
        studies = {}
        for s in studies_data:
            s['series'] = {}
            studies[s['id']] = s

        SeriesT = Series(self.conn)
        q = SeriesT.select('*').where(
            SeriesT.table.study_id.isin(list(studies.keys()))
        )
        series_data = await self.fetch(q)
        series_data = [dict(s) for s in series_data]
        for s in series_data:
            s['files'] = []
            studies[s['study_id']]['series'][s['id']] = s

        FilesT = Files(self.conn)
        q = FilesT.select('*').where(FilesT.table.study_id.isin(list(studies.keys())))
        files = await self.fetch(q)
        files = [dict(f) for f in files]
        for f in files:
            studies[f['study_id']]['series'][f['series_id']]['files'].append(f)

        for s in studies.values():
            s['series'] = list(s['series'].values())

        patient['studies'] = list(studies.values())
        return patient
