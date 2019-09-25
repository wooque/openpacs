# from multiprocessing import Process

import uvicorn
from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import FileResponse, UJSONResponse
from starlette.exceptions import HTTPException

import lifecycle
# import sync
from api.auth import TokenAuth
from api.routes import routes
from config import is_docker
# from dcm import server as dicom_server

app = Starlette(routes=routes)
app.add_middleware(AuthenticationMiddleware, backend=TokenAuth(), on_error=TokenAuth.on_auth_error)

sync_process = None
dcm_server = None


def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin,Accept,X-Auth-Pacs,Content-Type,X-Requested-With'


@app.middleware("http")
async def custom_middleware(request, call_next):
    response = await call_next(request)

    if response.status_code == 405:
        response.status_code = 200

    if is_docker and not request.url.path.startswith('/api') and response.status_code == 404:
        response = FileResponse('./static/index.html')

    add_cors(response)
    return response


@app.exception_handler(HTTPException)
async def http_exception(request, exc):
    resp = UJSONResponse({}, status_code=exc.status_code)
    add_cors(resp)
    return resp


@app.on_event('startup')
async def setup():
    await lifecycle.setup()


if __name__ == "__main__":
    # sync_process = Process(target=sync.main, daemon=True)
    # sync_process.start()
    #
    # dcm_server = Process(target=dicom_server.main, daemon=True)
    # dcm_server.start()

    uvicorn.run(app, host='localhost', port=8080)
