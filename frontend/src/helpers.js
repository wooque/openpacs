import { API_URL } from './config';
import history from './history';

export const handleResponse = async (response) => {
  if (!response) {
    return;
  }
  if (!response.ok && response.status !== 400) {
    const error = {error: response.status};
    throw error;
  }
  const json = await response.json();
  if (response.ok) {
    return json;
  } else {
    const error = {error: json};
    throw error;
  }
};

export const request = async (url, options = {}) => {
  if (!url.startsWith('http')) {
    url = `${API_URL}/${url}`;
  }
  let token = localStorage.getItem('token');
  if (!token) {
    token = localStorage.getItem('tempKey');
  }
  options.headers = new Headers({
    'X-Auth-Pacs': token,
  });
  // options.credentials = 'include';
  if (options.data) {
    options.method = 'POST';
    options.body = JSON.stringify(options.data);
    delete options.data;
  }
  if (options.query) {
    url = `${url}?${encodeQuery(options.query)}`;
    delete options.query;
  }
  try {
    const resp = await fetch(url, options);
    return await handleResponse(resp);
  } catch (error) {
    if (error.error === 401) {
      if (options.unauthorized) {
        options.unauthorized();
      }
      else {
        history.push('/login');
      }
    }
    // not aborted request
    if (!error.code || error.code !== 20) {
      throw Error(error.error || error.message || error);
    }
  }
};

export const open = async (url) => {
  return await request('files/download_token').then(data => {
    const token = data.token;
    if (url.includes('?')) {
      url = `${API_URL}/${url}&token=${token}`;
    } else {
      url = `${API_URL}/${url}?token=${token}`;
    }
    window.open(url);
  });
};

export const parseParams = search => {
  search = search.slice(1);
  let parts = search.split('&');
  let params = {};
  for (let part of parts) {
    let [name, value] = part.split('=');
    if (name) params[name] = value;
  }
  return params;
};

export const encodeQuery = data => {
  let ret = [];
  for (let d in data) {
    ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
  }
  return ret.join('&');
};

export const updateQuery = (history, data) => {
  let {pathname, search} = history.location;
  let params = parseParams(search);
  for (let k in data) {
    params[k] = data[k];
  }
  history.push(`${pathname}?${encodeQuery(params)}`);
};

export const emit = (event, data) => {
  let e = new CustomEvent(event, { detail: data });
  document.body.dispatchEvent(e);
};

export const subscribe = (event, listener) => {
  document.body.addEventListener(event, listener);
};

export const isAdmin = () => {
  return localStorage.getItem('admin') === 'true';
};
