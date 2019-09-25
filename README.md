# openpacs

Latest source code is at https://github.com/wooque/openpacs

## Install

### Easy way

Make sure you have `docker-compose` installed ([install docs](https://docs.docker.com/compose/install/))

Grab `docker-compose.yaml` file

Run `docker-compose up -d`

If you have trouble with elasticsearch container, complaining about permissions, run `chmod -R 1000 ./es`

### Custom installation 

#### Backend

Install and run `PostgreSQL` and `ElasticSearch`, easiest way is to run `docker-compose up -d` inside `backend` folder

Make sure you have `Python 3`, `gcc` and `make` installed

Create virtual environment `python -m venv venv`

Enter virtual environment `source venv/bin/activate`

Install dependencies `pip install -r requirements.txt`

Initialize database with `./manage db init`,
it will output random password that should be put wither in `DB_PASS` environment variable or `db_pass` field in `config.local.yaml`

Start processes `./start.sh`

### Frontend

Make sure you have `Node.js` and `npm` installed

Install dependencies `npm install`

Build frontend `npm run build`

Resulting files will be in `build` folder. 
Setup Nginx or some other webserver to serve files or copy files to `backend/static` folder and set `OPENPACS_DOCKER=true` environment variable to have backend serving files 
