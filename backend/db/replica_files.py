from datetime import datetime
import json

from dateutil.relativedelta import relativedelta
from pypika import Table as PyPikaTable, Query
from pypika.functions import Count
from pypika.terms import ValueWrapper

from db.table import Table


class Status:
    indexing = 0
    ok = 1
    deleted = 9


class ReplicaFiles(Table):
    name = 'replica_files'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS replica_files (
            id SERIAL,
            replica_id INTEGER NOT NULL REFERENCES replicas(id),
            file_id INTEGER NOT NULL REFERENCES files(id),
            location TEXT NOT NULL,
            status INTEGER NOT NULL,
            created TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            updated TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),            
            meta JSONB,
            UNIQUE (replica_id, file_id)
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS replica_files_replica_id 
        ON replica_files(replica_id);
        """)

    async def add(self, replica_id, files, status=Status.ok):
        async with self.conn.transaction():
            data = [
                (replica_id, f['id'], f['location'], status, json.dumps(f.get('meta', {})))
                for f in files
            ]
            q = self.insert().columns(
                'replica_id', 'file_id', 'location', 'status', 'meta'
            ).insert(*data).on_conflict('replica_id, file_id').do_nothing()

            await self.exec(q)

            q = Query.from_('replicas').select('*')
            replicas = await self.fetch(q)

            for r in replicas:
                data = [(r['id'], f['id'], '', Status.indexing) for f in files]

                q = self.insert().columns(
                    'replica_id', 'file_id', 'location', 'status',
                ).insert(*data).on_conflict('replica_id, file_id').do_nothing()

                await self.exec(q)

    async def add_replica(self, replica_id, master_id):
        rf = ReplicaFiles(alias='rfm')
        q = self.insert().columns(
            'replica_id', 'file_id', 'location', 'status',
        ).from_(rf.table).select(
            replica_id, rf.table.file_id, ValueWrapper(''), Status.indexing,
        ).where(rf.table.replica_id == master_id)
        await self.exec(q)

    async def delete_replica(self, replica_id):
        q = self.query().where(self.table.replica_id == replica_id).delete()
        await self.exec(q)

    async def count(self, replica_id):
        q = self.select(Count('1')).where(self.table.replica_id == replica_id)
        return await self.fetchval(q)

    async def non_indexing(self, replica_id):
        q = self.select(Count('1')).where(
            self.table.replica_id == replica_id,
        ).where(
            self.table.status != Status.indexing,
        )
        return await self.fetchone(q)

    async def get_for_file(self, file_id):
        q = self.select('*').where(self.table.file_id == file_id)
        return await self.fetch(q)

    async def get_for_sync(self, replica, offset=0):
        to_update = datetime.utcnow() - relativedelta(minutes=replica['delay'])

        files = PyPikaTable('files')
        q = self.select(
            self.table.replica_id, self.table.file_id, self.table.location,
            self.table.status, self.table.meta, files.name, files.hash,
        ).join(files).on(
            self.table.file_id == files.id
        ).where(
            self.table.replica_id == replica['id']
        ).where(
            self.table.status.isin([Status.indexing, Status.deleted])
        ).where(
            ((self.table.updated <= to_update) | (self.table.location == ''))
        ).orderby(self.table.id).offset(offset).limit(1000)

        return await self.fetch(q)

    async def get_file_from_replica(self, replica_id, file_id):
        Files = PyPikaTable('files')
        PatientT = PyPikaTable('patients')
        StudyT = PyPikaTable('studies')
        SeriesT = PyPikaTable('series')

        q = self.select(
            self.table.id, Files.name, Files.patient_id.as_('patient_db_id'),
            Files.study_id.as_('study_db_id'), Files.series_id.as_('series_db_id'),
            Files.hash, PatientT.patient_id, StudyT.study_id,
            SeriesT.number.as_('series_number'), Files.meta, Files.tools_state,
            self.table.location, self.table.status, self.table.meta.as_('replica_meta')
        ).join(Files).on(
            Files.id == self.table.file_id,
        ).join(PatientT).on(
            PatientT.id == Files.patient_id
        ).join(StudyT).on(
            StudyT.id == Files.study_id
        ).join(SeriesT).on(
            SeriesT.id == Files.series_id
        ).where(
            self.table.replica_id == replica_id,
        ).where(
            self.table.file_id == file_id,
        )
        data = await self.fetchone(q)
        if not data:
            return
        data = dict(data)
        data['meta'] = json.loads(data['meta'])
        data['replica_meta'] = json.loads(data['replica_meta'])
        return data

    async def index(self, replica_id, file):
        q = self.update().where(
            self.table.file_id == file['id'],
        ).where(
            self.table.replica_id == replica_id,
        ).set(
            self.table.location, file['location'],
        ).set(
            self.table.status, Status.ok,
        ).set(
            self.table.meta, json.dumps(file.get('meta', {})),
        )
        await self.exec(q)

    async def delete(self, replica_id, file_id):
        cnt = await self.count(replica_id)
        if cnt > 1:
            q = self.update().where(
                self.table.file_id == file_id,
            ).set(
                self.table.status, Status.deleted,
            ).set(
                self.table.updated, datetime.utcnow(),
            )
            await self.exec(q)

        q = self.query().where(
            self.table.replica_id == replica_id,
        ).where(
            self.table.file_id == file_id,
        ).delete()
        await self.exec(q)
        return cnt

    async def restore_deleted(self, replica_id):
        q = self.update().where(
            self.table.replica_id == replica_id
        ).where(
            self.table.status == Status.deleted,
        ).set(
            self.table.status, Status.ok
        ).returning('file_id')

        data = await self.fetch(q)
        if len(data):
            data = [d['file_id'] for d in data]
            files = PyPikaTable('files')
            q = files.update().where(files.id.isin(data)).set(
                files.indexed, False
            ).set(
                files.deleted, False,
            )
            await self.exec(q)
