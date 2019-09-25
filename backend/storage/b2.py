import asyncio
import concurrent.futures
import functools
import os.path
from io import BytesIO

from b2sdk.v1 import InMemoryAccountInfo, B2Api, DownloadDestBytes
from starlette.responses import StreamingResponse

from storage.storage import Storage

executor = concurrent.futures.ThreadPoolExecutor(4)


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(executor, lambda: f(*args, **kwargs))

    return inner


class B2Storage(Storage):
    name = 'b2'

    def __init__(self, replica):
        self.app_key_id = replica['meta']['app_key_id']
        self.app_key = replica['meta']['app_key']
        info = InMemoryAccountInfo()
        self.api = B2Api(info)
        self.bucket = 'openpacs'

    @staticmethod
    def default_config():
        return {
            'location': '',
        }

    @run_in_executor
    def init(self):
        self.api.authorize_account("production", self.app_key_id, self.app_key)
        try:
            self.api.create_bucket(self.bucket, 'allPrivate', cors_rules=[
                {
                    "corsRuleName": "downloadFromAnyOrigin",
                    "allowedOrigins": ["*"],
                    "allowedHeaders": ["*"],
                    "allowedOperations": [
                        "b2_download_file_by_id",
                        "b2_download_file_by_name"
                    ],
                    "maxAgeSeconds": 3600
                }
            ])
        except Exception as e:
            if 'Bucket name is already in use' not in str(e):
                raise

    @run_in_executor
    def index_(self):
        bucket = self.api.get_bucket_by_name(self.bucket)
        return bucket.api.session.list_file_names(bucket.id_, '', 1000, '')

    async def index(self):
        while True:
            resp = await self.index_()
            for entry in resp['files']:
                try:
                    patient_id, study_id, series_id, name = entry['fileName'].split('/')
                    if study_id == 'empty':
                        study_id = ''
                    if series_id == 'empty':
                        series_id = ''
                except:
                    continue
                yield {
                    'patient_id': patient_id,
                    'study_id': study_id,
                    'series_number': series_id,
                    'name': name,
                    'location': entry['fileName'],
                    'hash': entry['fileInfo'].get('hash'),
                }
            if resp['nextFileName'] is None:
                return

    def get_path(self, filedata):
        return os.path.join(
            str(filedata['patient_id']),
            str(filedata['study_id']) or 'empty',
            str(filedata['series_number']) or 'empty',
            filedata['name'],
        )

    @run_in_executor
    def copy(self, src, filedata):
        filename = self.get_path(filedata)
        bucket = self.api.get_bucket_by_name(self.bucket)
        file_info = {
            'hash': filedata['hash'],
        }
        id_ = None
        if isinstance(src, str):
            id_ = bucket.upload_local_file(
                local_file=src,
                file_name=filename,
                file_infos=file_info,
            )
        elif isinstance(src, BytesIO):
            id_ = bucket.upload_bytes(
                data_bytes=src.read(),
                file_name=filename,
                file_infos=file_info,
            )
        return {
            'location': filename,
            'meta': {
                'id': id_.id_,
            }
        }

    @run_in_executor
    def fetch(self, filedata):
        path = self.get_path(filedata)
        bucket = self.api.get_bucket_by_name(self.bucket)
        dest = DownloadDestBytes()
        bucket.download_file_by_name(path, dest)
        return BytesIO(dest.bytes_written)

    async def serve(self, file):
        bucket = self.api.get_bucket_by_name(self.bucket)
        # TODO: use this method if B2 fixes CORS
        # url = bucket.get_download_url(file['location'])
        # token = bucket.get_download_authorization(file['location'], 3600)
        # return RedirectResponse(url=f"{url}?Authorization={token}")
        fp = await self.fetch(file)
        return StreamingResponse(fp)

    @run_in_executor
    def delete(self, filedata):
        filename = self.get_path(filedata)
        self.api.delete_file_version(filedata['replica_meta']['id'], filename)
