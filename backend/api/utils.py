from datetime import datetime, timedelta

import jwt
from starlette.exceptions import HTTPException
from starlette.responses import UJSONResponse

from config import config


def gen_token(user, expire=None):
    payload = {
        'id': user['id'],
        'admin': user['admin'],
    }
    if not expire:
        expire = {'days': 14}

    exp = datetime.utcnow() + timedelta(**expire)
    payload['exp'] = exp

    return jwt.encode(
        payload,
        config['secret'],
        algorithm='HS256',
    )


def get_id(request):
    return int(request.path_params['id'])


def api_error(err):
    return UJSONResponse({'error': str(err)}, status_code=400)


def is_admin(request):
    if not request.user.admin:
        raise HTTPException(status_code=403)
