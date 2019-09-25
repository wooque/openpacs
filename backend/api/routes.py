from starlette.routing import Router, Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from api.patient import PatientHandler
from api.files import (
    Upload, DownloadFiles, DownloadData, DownloadToken, FilesHandler, FileHandler,
    FileChangesHandler, ShareFilesHandler, ServeFile
)
from api.logs import LogsHandler
from api.replicas import ReplicasHandlers, ReplicaHandlers
from api.users import (
    Login, ChangePassword, UsersHandler, UsersDeactivate, UsersNewPassword,
)
from api.ws import WSToken, WebsocketHandler
from config import is_docker

routes = [
    Route('/replicas', endpoint=ReplicasHandlers),
    Route('/replicas/{id}', endpoint=ReplicaHandlers),
    Route('/login', endpoint=Login),
    Route('/change_password', endpoint=ChangePassword),
    Route('/users', endpoint=UsersHandler),
    Route('/users/deactivate', endpoint=UsersDeactivate),
    Route('/users/new_password', endpoint=UsersNewPassword),
    Route('/patients/{id}', endpoint=PatientHandler),
    Route('/files/upload', endpoint=Upload),
    Route('/files/download_token', endpoint=DownloadToken),
    Route('/files/download.zip', endpoint=DownloadFiles),
    Route('/files/download.csv', endpoint=DownloadData),
    Route('/files', endpoint=FilesHandler),
    Route('/files/{id}', endpoint=FileHandler),
    Route('/files/{id}/changes', endpoint=FileChangesHandler),
    Route('/files/{id}/share', endpoint=ShareFilesHandler),
    Route('/files/{id}/data', endpoint=ServeFile),
    Route('/logs', endpoint=LogsHandler),
    Route('/ws_token', endpoint=WSToken),
    WebSocketRoute('/ws', endpoint=WebsocketHandler)
]
routes = [
    Mount('/api', app=Router(routes)),
]
if is_docker:
    routes.append(Mount('/', app=StaticFiles(directory='static'), name="static"))
