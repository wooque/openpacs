from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse

from api.utils import is_admin
from db.conn import get_conn
from db.replica import Replica
from db.replica_files import ReplicaFiles


class ReplicasHandlers(HTTPEndpoint):
    async def post(self, request):
        is_admin(request)
        data = await request.json()

        async with get_conn()as conn:
            async with conn.transaction():
                replica = Replica(conn)
                result = await replica.add(data['type'], data)

                master = await replica.master()
                if not master:
                    master_id = result
                    await replica.set_master(result)
                else:
                    master_id = master['id']

                await ReplicaFiles(conn).add_replica(result, master_id)

        return UJSONResponse({'id': result})

    async def get(self, request):
        is_admin(request)
        async with get_conn() as conn:
            replicas = await Replica(conn).get_all()

        return UJSONResponse({'data': replicas})


class ReplicaHandlers(HTTPEndpoint):
    async def post(self, request):
        is_admin(request)
        data = await request.json()
        replica_id = int(request.path_params['id'])

        async with get_conn() as conn:
            if 'master' in data:
                await Replica(conn).set_master(replica_id)
            if 'delay' in data:
                await Replica(conn).update_delay(replica_id, data['delay'])

        return UJSONResponse({})

    async def delete(self, request):
        is_admin(request)
        replica_id = int(request.path_params['id'])

        async with get_conn() as conn:
            await Replica(conn).delete(replica_id)

        return UJSONResponse({})
