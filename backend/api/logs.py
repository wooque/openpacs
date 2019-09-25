from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse

from api.utils import is_admin
from db.conn import get_conn
from db.log import Log


class LogsHandler(HTTPEndpoint):
    async def get(self, request):
        is_admin(request)
        offset = request.path_params.get('offset')
        limit = request.path_params.get('limit')

        async with get_conn() as conn:
            data = await Log(conn).get_logs(offset=offset, limit=limit)
        return UJSONResponse({'data': [dict(u) for u in data]})
