import sys
import time

from es import es
import db.conn
from db.users import Users
from db.table import Table


async def setup(db_pool_size=None, sync_db=False):
    success = False
    for i in range(30):
        try:
            await db.conn.setup(pool_size=db_pool_size)
            await es.setup()
            success = True
            break
        except Exception as e:
            print(e)
            # try teardown and retry
            try:
                await teardown()
            except:
                pass
        time.sleep(1)

    if not success:
        print("Can't connect to database or elasticsearch")
        sys.exit(1)

    if sync_db:
        async with db.conn.get_conn() as conn:
            for t in Table.tables:
                try:
                    await t(conn).sync_db()
                except:
                    print(f"{t.name} failed")
                    raise

            await Users(conn).add_superadmin()


async def teardown():
    await db.conn.teardown()
    await es.teardown()
