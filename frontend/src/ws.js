import { API_URL } from './config';
import { request } from './helpers';

let ws;
let onOpenFunc;
let messageFunc;

export function init() {
  request('ws_token').then((data) => {
    const au = API_URL.split('//')[1];
    ws = new WebSocket(`ws://${au}/ws?token=${data.token}`);
    ws.addEventListener('open', function () {
      if (onOpenFunc) onOpenFunc();
    });
    ws.addEventListener('message', function (event) {
      if (messageFunc) messageFunc(JSON.parse(event.data));
    });
    ws.addEventListener('close', function () {
      init();
    });
  }).catch(e => {
    console.error(e);
  });
}

export function onOpen(func) {
  onOpenFunc = func;
  if (!ws) return;
  ws.addEventListener('open', function () {
    onOpenFunc();
  });
}

export function addEventListener(func) {
  messageFunc = func;
  if (!ws) return;
  ws.addEventListener('message', function (event) {
    func(JSON.parse(event.data));
  });
}

export function send(msg) {
  if (!ws) return;
  ws.send(JSON.stringify(msg));
}