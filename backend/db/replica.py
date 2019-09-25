import json

from db.replica_files import ReplicaFiles
from storage.storage import Storage
from db.table import Table
from db.files import Files

from pypika.functions import Count


class Replica(Table):
    name = 'replicas'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS replicas (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
            location TEXT NOT NULL UNIQUE,
            master BOOLEAN NOT NULL DEFAULT FALSE,
            delay INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            total INTEGER NOT NULL DEFAULT 0,
            meta JSONB
        );
        """)
        await self.exec("""
        CREATE UNIQUE INDEX IF NOT EXISTS replicas_master_unique 
        ON replicas(master) WHERE master = TRUE;
        """)
        await self.exec("""
        CREATE OR REPLACE FUNCTION notify_event() RETURNS TRIGGER AS $$
          DECLARE
            record RECORD;
            payload JSON;
          BEGIN
            IF (TG_OP = 'DELETE') THEN
              record = OLD;
            ELSE
              record = NEW;
            END IF;
        
            payload = json_build_object('table', TG_TABLE_NAME,
                                        'action', TG_OP,
                                        'old', row_to_json(OLD),
                                        'new', row_to_json(NEW));
        
            PERFORM pg_notify('events', payload::text);
        
            RETURN NULL;
          END;
          $$ LANGUAGE plpgsql;
        """)
        await self.exec("""
        DROP TRIGGER IF EXISTS notify_replica_event ON replicas
        """)
        await self.exec("""
        CREATE TRIGGER notify_replica_event
        AFTER INSERT OR UPDATE OR DELETE ON replicas
          FOR EACH ROW EXECUTE PROCEDURE notify_event();
        """)

    @staticmethod
    def to_json(data):
        data = dict(data)
        if data['meta']:
            data['meta'] = json.loads(data['meta'])
        return data

    async def add(self, type_, data):
        default_config = Storage.default_config_by_type(type_)
        location = data.get('location')
        if not location:
            location = default_config.get('location')

        q = self.insert().columns(
            self.table.type, self.table.delay, self.table.location,
            self.table.status, self.table.meta,
        ).insert(
            type_, data['delay'], location, 'indexing', json.dumps(data),
        ).returning(self.table.id)

        return await self.fetchval(q)

    async def master(self):
        q = self.select('*').where(self.table.master == True)
        data = await self.fetchone(q)
        return self.to_json(data) if data else None

    async def set_master(self, replica_id):
        async with self.conn.transaction():
            q = self.update().where(
                self.table.id != replica_id
            ).set(self.table.master, False)

            await self.exec(q)

            q = self.update().where(
                self.table.id == replica_id
            ).set(
                self.table.master, True
            ).set(
                self.table.delay, 0
            ).set(
                self.table.status, 'indexing',
            )
            await self.exec(q)

            await ReplicaFiles(self.conn).restore_deleted(replica_id)

    async def get(self, replica_id):
        q = self.select('*').where(
            self.table.id == replica_id,
        )
        return await self.fetchone(q)

    async def get_all(self):
        q = self.select('*').orderby(self.table.id)
        data = await self.fetch(q)
        data = [dict(d) for d in data]

        for d in data:
            d['files'] = await ReplicaFiles(self.conn).non_indexing(d['id'])
            d['meta'] = json.loads(d['meta'] or '{}')

        return data

    async def delete(self, replica_id):
        async with self.conn.transaction():
            await ReplicaFiles(self.conn).delete_replica(replica_id)

            q = self.query().where(self.table.id == replica_id).delete()
            await self.exec(q)

            q = self.select(Count('1'))
            cnt = await self.fetchval(q)
            if cnt == 0:
                await Files(self.conn).delete_all()

    async def update_status(self, replica_id, status):
        q = self.update().where(
            self.table.id == replica_id,
        ).set(self.table.status, status)

        await self.exec(q)

    async def update_total(self, replica_id, total):
        q = self.update().where(
            self.table.id == replica_id,
        ).set(self.table.total, total)

        await self.exec(q)

    async def update_delay(self, replica_id, delay):
        q = self.update().where(
            self.table.id == replica_id,
        ).set(self.table.delay, delay)

        await self.exec(q)
