import asyncio
import signal
import sys
import traceback
import uuid
from io import BytesIO

from pynetdicom import AE, evt, StoragePresentationContexts

from db.conn import get_conn
from db.files import Files
from db.log import Log
from db.replica import Replica
from db.replica_files import ReplicaFiles
from dcm.file import get_meta
from lifecycle import setup, teardown
from storage.storage import Storage
from utils import hash_file

initialized = False
loop = None


async def store(ds, data):
    global initialized

    if not initialized:
        await setup()
        initialized = True

    async with get_conn() as conn:
        try:
            ds = get_meta(ds)
            async with conn.transaction():
                master = await Replica(conn).master()

                hsh = hash_file(data)

                file_data = {
                    'name': str(uuid.uuid4()) + '.dcm',
                    'master': master['id'],
                    'hash': hsh,
                }
                file_data.update(ds)
                f = await Files(conn).insert_or_select(file_data)

                storage = await Storage.get(master)
                ret = await storage.copy(data, f)

                await ReplicaFiles(conn).add(
                    master['id'],
                    [{'id': f['id'], **ret}],
                )
        except Exception as e:
            print(traceback.format_exc())
            await Log(conn).add(str(e))
            return False
    return True


def handle_store(event):
    global loop

    ds = event.dataset
    ds.file_meta = event.file_meta
    dst = BytesIO()

    try:
        ds.save_as(dst, write_like_original=False)

        if not loop:
            loop = asyncio.new_event_loop()
        result = loop.run_until_complete(store(ds, dst))
        if not result:
            return 0x0001

    except Exception as e:
        print(traceback.format_exc())
        return 0x0001

    return 0x0000


handlers = [(evt.EVT_C_STORE, handle_store)]
scp = None


def signal_handler(sig, frame):
    global loop

    if scp:
        scp.shutdown()

    if loop:
        loop.run_until_complete(teardown())
    sys.exit(0)


def main():
    global scp

    signal.signal(signal.SIGINT, signal_handler)
    ae = AE()
    ae.supported_contexts = StoragePresentationContexts
    scp = ae.start_server(('', 11112), evt_handlers=handlers)
