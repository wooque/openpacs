import asyncio

from db.conn import get_conn
from db.files import Files
from es.es import index_file, reset_index
from lifecycle import setup, teardown


async def reindex_main():
    await setup(sync_db=True)

    await reset_index()

    async with get_conn() as conn:
        files = await Files(conn).get_all()

    for f in files:
        await index_file(f)

    await teardown()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reindex_main())
