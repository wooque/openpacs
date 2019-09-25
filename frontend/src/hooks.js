import { useState, useEffect, useRef } from 'react';
import { LOADING_DELAY, API_URL } from './config';
import { handleResponse } from './helpers';
import history from './history';

export function useFetch(url, options = {}) {
  // TODO: optimize with reducer?
  const [loading, setLoading] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const controller = useRef();

  if (!url.startsWith('http')) {
    url = `${API_URL}/${url}`;
  }
  const exec = async (doShowLoading = true, execOptions = {}) => {
    if (controller.current) {
      controller.current.abort();
    }
    setLoading(true);
    let loaderTimeout;
    if (doShowLoading) {
      loaderTimeout = setTimeout(
        () => setShowLoading(true),
        LOADING_DELAY,
      );
    }
    const finish = () => {
      if (doShowLoading) {
        clearTimeout(loaderTimeout);
        setShowLoading(false);
      }
      setLoading(false);
    };

    // options.credentials = 'include';
    options.headers = new Headers({
      'X-Auth-Pacs': localStorage.getItem('token'),
    });
    controller.current = new AbortController();
    options.signal = controller.current.signal;
    try {
      const resp = await fetch(url, Object.assign({}, options, execOptions));
      const data = await handleResponse(resp);
      setData(data);
      finish();
    }
    catch (error) {
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
        setError(error.error || error.message || error);
      }
      finish();
    }
  };
  return {exec, loading, showLoading, data, error, controller};
}

export function useFormInput(initalState) {
  const [value, setValue] = useState(initalState);

  return {
    value: value,
    onChange: (e) => {
      if (e.target) {
        setValue(e.target.value);
      } else {
        setValue(e);
      }
    }
  };
}

export function usePrevious(value) {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
}
