from datetime import datetime
import json

from es import es
from db.patient import Patient
from db.study import Study
from db.series import Series
from db.replica_files import ReplicaFiles
from db.table import Table
from db.file_changes import FileChange


class Files(Table):
    name = 'files'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER NOT NULL REFERENCES patients(id),
            study_id INTEGER NOT NULL REFERENCES studies(id),
            series_id INTEGER NOT NULL REFERENCES series(id),
            name TEXT NOT NULL,
            indexed BOOLEAN NOT NULL DEFAULT FALSE,
            hash TEXT NOT NULL,
            created TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            updated TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            deleted BOOLEAN NOT NULL DEFAULT FALSE,
            meta JSONB,
            tools_state JSONB
        );
        """)
        await self.exec('CREATE INDEX IF NOT EXISTS files_name on files(name);')
        await self.exec('CREATE INDEX IF NOT EXISTS files_hash on files(hash);')

    @staticmethod
    def from_row(file):
        file = dict(file)
        if file.get('meta'):
            file['meta'] = json.loads(file['meta'])

        if file.get('tools_state'):
            file['tools_state'] = json.loads(file['tools_state'])
        return file

    async def add(self, filedata):
        async with self.conn.transaction():
            patient = await Patient(self.conn).insert_or_select(filedata)
            filedata['patient_db_id'] = patient['id']
            study = await Study(self.conn).insert_or_select(filedata)
            filedata['study_db_id'] = study['id']
            series = await Series(self.conn).insert_or_select(filedata)
            filedata['series_db_id'] = series['id']

            now = datetime.utcnow()
            q = self.insert().columns(
                'name', 'patient_id', 'study_id', 'series_id', 'meta',
                'indexed', 'hash', 'created', 'updated',
            ).insert((
                filedata['name'], patient['id'], study['id'], series['id'], json.dumps(filedata['cleaned']),
                False, filedata['hash'], now, now,
            ), ).returning('id')

            file_id = await self.fetchval(q)

        filedata['id'] = file_id
        filedata['meta'] = filedata['cleaned']
        await es.index_file(filedata)

        q = self.update().where(self.table.id == file_id).set(self.table.indexed, True)
        await self.exec(q)

        return filedata

    async def get(self, filedata):
        PatientT = Patient().table
        StudyT = Study().table
        SeriesT = Series().table
        table = self.table

        q = self.select(
            table.id, table.name,
            table.patient_id.as_('patient_db_id'),
            table.study_id.as_('study_db_id'),
            table.series_id.as_('series_db_id'),
            PatientT.patient_id,
            StudyT.study_id,
            SeriesT.number.as_('series_number'),
        ).join(PatientT).on(
            PatientT.id == table.patient_id
        ).join(StudyT).on(
            StudyT.id == table.study_id
        ).join(SeriesT).on(
            SeriesT.id == table.series_id
        ).where(
            PatientT.patient_id == filedata['patient_id'],
        ).where(
            StudyT.study_id == filedata['study_id'],
        ).where(
            SeriesT.number == filedata['series_number'],
        ).where(
            self.table.name == filedata['name']
        )
        return await self.fetchone(q)

    async def insert_or_select(self, filedata):
        f = await self.get(filedata)
        if f:
            return f
        return await self.add(filedata)

    def q(self):
        PatientT = Patient().table
        StudyT = Study().table
        SeriesT = Series().table
        table = self.table

        return self.select(
            table.id, table.name,
            table.patient_id.as_('patient_db_id'),
            table.study_id.as_('study_db_id'),
            table.series_id.as_('series_db_id'),
            PatientT.patient_id,
            StudyT.study_id,
            SeriesT.number.as_('series_number'),
            table.meta, table.tools_state, table.deleted,
        ).join(PatientT).on(
            PatientT.id == table.patient_id
        ).join(StudyT).on(
            StudyT.id == table.study_id
        ).join(SeriesT).on(
            SeriesT.id == table.series_id
        )

    async def get_extra(self, file_id):
        q = self.q().where(self.table.id == file_id)
        file = await self.fetchone(q)
        if not file:
            return None

        file = self.from_row(file)

        file['patient'] = await Patient(self.conn).get_extra(file['patient_db_id'])

        data = await ReplicaFiles(self.conn).get_for_file(file_id)
        file['files'] = [dict(d) for d in data]

        return file

    async def get_all(self):
        q = self.q()
        files = await self.fetch(q)
        return [self.from_row(f) for f in files]

    async def unindexed(self):
        q = self.q().where(self.table.indexed == False)
        files = await self.fetch(q)
        return [self.from_row(f) for f in files]

    async def update_tools_state(self, file_id, user_id, data):
        q = self.update().where(
            self.table.id == file_id,
        ).set(
            self.table.tools_state, json.dumps(data),
        )
        await self.exec(q)
        await FileChange(self.conn).add_change(file_id, 'anotations changed', user_id)

    async def update_tag(self, file_id, user_id, data):
        async with self.conn.transaction():
            q = self.select('meta').where(self.table.id == file_id)
            meta = await self.fetchval(q)
            meta = json.loads(meta)

            old = meta[data['key']]
            new = data['value']
            meta[data['key']] = new

            q = self.update().where(self.table.id == file_id).set(self.table.meta, json.dumps(meta))
            await self.exec(q)

            await FileChange(self.conn).add_change(file_id, data['key'], user_id, old, new)

    async def get_by_hash(self, hash):
        q = self.select('*').where(self.table.hash == hash)
        return await self.fetchone(q)

    async def delete(self, file_id, master_id):
        await es.delete(file_id)

        async with self.conn.transaction():
            q = self.update().where(self.table.id == file_id).set(self.table.deleted, True)
            await self.exec(q)
            cnt = await ReplicaFiles(self.conn).delete(master_id, file_id)
            if cnt == 1:
                q = self.query().where(self.table.id == file_id).delete()
                await self.exec(q)

    async def delete_all(self):
        await es.reset_index()
        q = self.query().delete()
        await self.exec(q)
