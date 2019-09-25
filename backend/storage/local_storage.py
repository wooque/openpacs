import os
import os.path
import shutil

from starlette.responses import FileResponse

from storage.storage import Storage
from utils import hash_file


class LocalStorage(Storage):
    name = 'local'

    def __init__(self, replica):
        self.location = replica['location']
        if self.location.endswith('/'):
            self.location = self.location[:-1]

    @staticmethod
    def default_config():
        return {
            'location': os.path.abspath('../data/files'),
        }

    async def init(self):
        if not os.path.exists(self.location):
            os.makedirs(self.location)

    async def index(self):
        for root, dirs, files in os.walk(self.location):
            for f in files:
                full_path = os.path.join(root, f)
                try:
                    parts = root.replace(self.location + '/', '').split('/')
                    patient_id, study_id, series_id = parts
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
                    'name': f,
                    'location': full_path,
                }

    def _copy(self, src, dst):
        if isinstance(src, str):
            shutil.copyfile(src, dst)
        else:
            src.seek(0)
            with open(dst, 'wb') as f:
                shutil.copyfileobj(src, f)

    def get_path(self, filedata):
        return os.path.join(
            str(filedata['patient_id']),
            str(filedata['study_id']) or 'empty',
            str(filedata['series_number']) or 'empty',
            filedata['name'],
        )

    async def copy(self, src, filedata):
        dst = self.get_path(filedata)
        dst = os.path.join(self.location, dst)

        dir = os.path.dirname(dst)
        if not os.path.exists(dir):
            os.makedirs(dir)

        try:
            self._copy(src, dst)
        except PermissionError:
            # try adding writable permissions
            os.chmod(dst, 644)
            self._copy(src, dst)
        return {
            'location': dst
        }

    def hash(self, location):
        with open(location, 'rb') as dcmf:
            return hash_file(dcmf)

    async def fetch(self, filedata):
        return os.path.join(self.location, self.get_path(filedata))

    async def serve(self, filedata):
        path = os.path.join(self.location, self.get_path(filedata))
        return FileResponse(path)

    async def delete(self, filedata):
        path = os.path.join(self.location, self.get_path(filedata))
        try:
            os.remove(path)
        except Exception as e:
            if 'No such file' not in str(e):
                raise
