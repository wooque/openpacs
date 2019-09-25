from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse

from api.utils import gen_token, is_admin
from db.conn import get_conn
from db.users import Users
from exeptions import ApiException


class Login(HTTPEndpoint):
    async def post(self, request):
        data = await request.json()

        async with get_conn() as conn:
            try:
                data = await Users(conn).login(data['username'], data['password'])
            except ApiException as e:
                return UJSONResponse({'error': str(e)}, status_code=400)

            token = gen_token(data)
            resp = UJSONResponse({
                'id': data['id'],
                'admin': data['admin'],
                'token': token,
            })
            return resp


class ChangePassword(HTTPEndpoint):
    async def post(self, request):
        data = await request.json()

        async with get_conn() as conn:
            try:
                data = await Users(conn).change_password(request.user, data['password'])
            except ApiException as e:
                return UJSONResponse({'error': str(e)}, status_code=400)

            return UJSONResponse({})


class UsersHandler(HTTPEndpoint):
    async def get(self, request):
        is_admin(request)
        q = request.path_params.get('q')
        offset = request.path_params.get('offset')
        limit = request.path_params.get('limit')

        async with get_conn() as conn:
            data = await Users(conn).get_users(offset=offset, limit=limit, username=q)

        return UJSONResponse({'data': [Users.to_json(u) for u in data]})

    async def post(self, request):
        is_admin(request)
        data = await request.json()

        async with get_conn() as conn:
            result = await Users(conn).add_user(data['username'], data['admin'])

        return UJSONResponse({'password': result['password'], 'username': data['username']})


class UsersDeactivate(HTTPEndpoint):
    async def post(self, request):
        is_admin(request)
        data = await request.json()

        async with get_conn() as conn:
            await Users(conn).deactivate(data['id'])

        return UJSONResponse({})


class UsersNewPassword(HTTPEndpoint):
    async def post(self, request):
        is_admin(request)
        data = await request.json()

        async with get_conn() as conn:
            result = await Users(conn).new_pswd(data['id'])

        return UJSONResponse({'password': result})
