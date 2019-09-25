import csv
import os.path
from zipfile import ZipFile
from uuid import uuid4

from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse, FileResponse
from starlette.exceptions import HTTPException
from starlette.background import BackgroundTask

from api.utils import get_id, api_error, is_admin, gen_token
from db.conn import get_conn
from db.file_changes import FileChange
from db.files import Files
from db.replica import Replica
from db.replica_files import ReplicaFiles
from db.share_files import SharedFiles
from dcm.file import parse_dcm
from es import es
from storage.storage import Storage
from utils import hash_file


class Upload(HTTPEndpoint):
    async def post(self, request):
        form = await request.form()
        filename = form['file'].filename
        file = form['file'].file

        async with get_conn() as conn:
            async with conn.transaction():
                master = await Replica(conn).master()
                if not master:
                    return api_error('No master set')

                ds = parse_dcm(file)
                hsh = hash_file(file)

                file_data = {
                    'name': os.path.basename(filename),
                    'master': master['id'],
                    'hash': hsh,
                }
                file_data.update(ds)
                filedata = await Files(conn).insert_or_select(file_data)

                storage = await Storage.get(master)
                ret = await storage.copy(file, filedata)

                await ReplicaFiles(conn).add(
                    master['id'],
                    [{'id': filedata['id'], **ret}],
                )
        return UJSONResponse({})


def zip_files(files, zipname):
    with ZipFile(zipname, 'w') as myzip:
        for f in files:
            if isinstance(f['tmp'], str):
                myzip.write(f['tmp'], arcname=f['arcname'])
            else:
                myzip.writestr(f['arcname'], data=f['tmp'].read())


class DownloadFiles(HTTPEndpoint):
    async def get(self, request):
        data = [int(i) for i in request.query_params['ids'].split(',')]
        files = []
        async with get_conn() as conn:
            master = await Replica(conn).master()
            storage = await Storage.get(master)

            for d in data:
                file = await ReplicaFiles(conn).get_file_from_replica(master['id'], d)
                tmp = await storage.fetch(file)
                file['tmp'] = tmp
                file['arcname'] = '_'.join([
                    str(file['patient_id']),
                    str(file['study_id']) or 'empty',
                    str(file['series_number']) or 'empty',
                    file['name'],
                ])
                files.append(file)

        tmp = uuid4()
        zipname = f'/tmp/{tmp}.zip'
        await BackgroundTask(zip_files, files, zipname)()
        return FileResponse(zipname)


class DownloadData(HTTPEndpoint):
    async def get(self, request):
        data = [int(i) for i in request.query_params['ids'].split(',')]
        columns = set([])
        rows = []
        async with get_conn() as conn:
            master = await Replica(conn).master()

            for d in data:
                file = await ReplicaFiles(conn).get_file_from_replica(master['id'], d)
                columns.update(file['meta'].keys())
                rows.append(file['meta'])

        columns = list(columns)
        columns.sort()
        tmp = uuid4()
        tmp_csv = f'/tmp/{tmp}.csv'
        with open(tmp_csv, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(columns)

            for r in rows:
                row = [r.get(c, '') for c in columns]
                csvwriter.writerow(row)

        return FileResponse(tmp_csv)


class FilesHandler(HTTPEndpoint):
    async def post(self, request):
        data = await request.json()

        async with get_conn() as conn:
            data = await es.search(data)
            return UJSONResponse(data)


async def get_file_by_id(request):
    file_id = int(request.path_params['id'])
    async with get_conn() as conn:
        file = await Files(conn).get_extra(file_id)
        if not file or file['deleted']:
            raise HTTPException(status_code=404)
        return file


class FileHandler(HTTPEndpoint):
    async def get(self, request):
        data = await get_file_by_id(request)
        if not data:
            return UJSONResponse(status_code=404)
        return UJSONResponse(data)

    async def post(self, request):
        file_id = get_id(request)
        data = await request.json()
        if 'tools_state' in data:
            async with get_conn() as conn:
                await Files(conn).update_tools_state(
                    file_id,
                    request.user.id,
                    data['tools_state'],
                )
        return UJSONResponse(data)

    async def delete(self, request):
        is_admin(request)
        async with get_conn() as conn:
            async with conn.transaction():
                master = await Replica(conn).master()
                if not master:
                    return api_error('No master set')

                file = await get_file_by_id(request)
                storage = await Storage.get(master)
                await storage.delete(file)

                await Files(conn).delete(file['id'], master['id'])
        return UJSONResponse({})


class FileChangesHandler(HTTPEndpoint):
    async def get(self, request):
        file_id = get_id(request)
        async with get_conn() as conn:
            data = await FileChange(conn).for_file(file_id)

        return UJSONResponse({'data': data})


class ServeFile(HTTPEndpoint):
    async def get(self, request):
        file_id = get_id(request)
        if not file_id:
            raise HTTPException(status_code=404)

        async with get_conn() as conn:
            master = await Replica(conn).master()
            file = await ReplicaFiles(conn).get_file_from_replica(master['id'], file_id)
            storage = await Storage.get(master)

        if not file:
            raise HTTPException(status_code=404)
        return await storage.serve(file)


class ShareFilesHandler(HTTPEndpoint):
    async def post(self, request):
        file_id = get_id(request)
        data = await request.json()

        async with get_conn() as conn:
            key = await SharedFiles(conn).share(file_id, data['duration'])
        return UJSONResponse({'key': key})


class DownloadToken(HTTPEndpoint):
    async def get(self, request):
        token = gen_token(request.user.to_dict(), {'minutes': 1})
        return UJSONResponse({'token': token})
