from collections import defaultdict
from threading import Lock

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import UJSONResponse
from starlette.websockets import WebSocket

from api.utils import gen_token


class WSToken(HTTPEndpoint):
    async def get(self, request):
        token = gen_token(request.user.to_dict(), {'minutes': 1})
        return UJSONResponse({'token': token})


files = defaultdict(lambda: {'ver': 0, 'state': None})
mutex = Lock()


class WebsocketHandler(WebSocketEndpoint):
    encoding = 'json'

    async def on_connect(self, websocket):
        await websocket.accept()

    async def on_receive(self, websocket, data):
        type_ = data.get('type')

        if type_ == 'open':
            f = data['file']
            state = None
            mutex.acquire()
            try:
                files[f][id(websocket)] = websocket
                if files[f]['state']:
                    state = files[f]['state']
            finally:
                mutex.release()

            if state:
                await websocket.send_json(
                    {
                        'type': 'send_state',
                        'file': f,
                        'state': state,
                    },
                )
            websocket.file = f

        elif type_ == 'send_state':
            f = data['file']
            conns = []

            mutex.acquire()
            try:
                fdata = files.get(f, {})
                fdata['state'] = data['state']
                fdata['ver'] = fdata['ver'] + 1

                conns = list(fdata.values())
            finally:
                mutex.release()

            for c in conns:
                if c == websocket: continue
                if not isinstance(c, WebSocket): continue
                await c.send_json(data)

    async def on_disconnect(self, websocket, close_code):
        f = getattr(websocket, 'file', None)
        if f:
            mutex.acquire()
            try:
                del files[f][id(websocket)]
            except:
                pass
            finally:
                mutex.release()
