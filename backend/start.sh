python db_init.py
python dcm_server.py &
python sync.py &
gunicorn app:app -k uvicorn.workers.UvicornWorker -c api_conf.py