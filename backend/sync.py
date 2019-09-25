import asyncio
import json
import time
import traceback

from db.conn import get_conn, create_conn
from db.files import Files
from db.log import Log
from db.replica import Replica
from db.replica_files import ReplicaFiles, Status
from dcm.file import parse_dcm
from es.es import index_file
from lifecycle import setup, teardown
from storage.storage import Storage
from utils import hash_file

work = True


async def index(replica):
    global work

    replica_id = replica['id']
    async with get_conn() as conn:
        await Replica(conn).update_status(replica_id, 'indexing')

        storage = await Storage.get(replica)

        indexing_interrupted = False
        async for d in storage.index():
            if not work:
                indexing_interrupted = True
                break

            loc = None
            if not d.get('hash'):
                loc = await storage.fetch(d)

                if not d.get('hash'):
                    d['hash'] = hash_file(loc)

            f = await Files(conn).get(d)
            if not f:
                if not replica['master']:
                    continue
                if not loc:
                    loc = await storage.fetch(d)
                try:
                    dcm_data = parse_dcm(loc)
                except Exception as e:
                    continue

                d.update(dcm_data)
                d['master'] = replica['id']

                f = await Files(conn).add(d)

            d['id'] = f['id']
            try:
                del d['meta']
            except KeyError:
                pass
            if replica['master']:
                await ReplicaFiles(conn).add(replica_id, [d], )
            else:
                await ReplicaFiles(conn).index(replica_id, d)

        files = await ReplicaFiles(conn).get_for_sync(replica)
        if len(files) == 0 and not indexing_interrupted:
            await Replica(conn).update_status(replica_id, 'ok')


async def do_sync():
    global work

    # index unindexed files
    async with get_conn() as conn:
        files = await Files(conn).unindexed()

    for f in files:
        if not work:
            return
        await index_file(f)

    replicas = {}
    master = {}

    async with get_conn() as conn:
        data = await Replica(conn).get_all()
        for d in data:
            if d['master']:
                master = dict(d)
            replicas[d['id']] = dict(d)

    for r in replicas.values():
        storage = await Storage.get(r)
        r['storage'] = storage
        if r['master']:
            master['storage'] = storage

    for r in replicas.values():
        if not work:
            return

        if r['status'] == 'indexing':
            await index(r)

        if r['master']:
            continue

        offset = 0
        while True:
            async with get_conn() as conn:
                data = await ReplicaFiles(conn).get_for_sync(r, offset)

                if len(data):
                    await Replica(conn).update_status(r['id'], 'syncing')

                for d in data:
                    if not work:
                        return

                    if d['status'] == Status.deleted:
                        rf = await ReplicaFiles(conn).get_file_from_replica(
                            r['id'],
                            d['file_id'],
                        )
                        await r['storage'].delete(rf)
                        await ReplicaFiles(conn).delete(r['id'], d['file_id'])
                    else:
                        rfm = await ReplicaFiles(conn).get_file_from_replica(
                            master['id'],
                            d['file_id'],
                        )
                        local_loc = await master['storage'].fetch(rfm)

                        ret = await r['storage'].copy(local_loc, rfm)
                        await ReplicaFiles(conn).index(r['id'], {'id': d['file_id'], **ret})

            if len(data) < 1000:
                if len(data):
                    async with get_conn() as conn:
                        await Replica(conn).update_status(r['id'], 'ok')
                break
            offset += 1000


listener_conn = None


def db_event(conn, pid, channel, payload):
    global work
    data = json.loads(payload)
    if data['action'] == 'UPDATE':
        diff = [k for k in data['old'] if data['new'][k] != data['old'][k]]
        if len(diff) == 0 or (len(diff) == 1 and diff[0] == 'status'):
            return
    work = False


async def sync():
    global listener_conn, work

    await setup()

    listener_conn = await create_conn()
    await listener_conn.add_listener('events', db_event)

    while True:
        work = True
        try:
            await do_sync()
        except Exception as e:
            print(traceback.format_exc())
            try:
                async with get_conn() as conn:
                    await Log(conn).add(traceback.format_exc())
            except Exception as e:
                print(traceback.format_exc())
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            if listener_conn:
                await listener_conn.close()
            await teardown()
            break


def main():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(sync())
    loop.close()


if __name__ == '__main__':
    main()
