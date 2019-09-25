import asyncio
import os.path
from io import BytesIO
from tempfile import SpooledTemporaryFile

import aiobotocore
from starlette.responses import StreamingResponse

from storage.storage import Storage


class S3Storage(Storage):
    name = 's3'

    def __init__(self, replica):
        self.access_key_id = replica['meta']['access_key_id']
        self.secret_access_key = replica['meta']['secret_access_key']
        loop = asyncio.get_running_loop()
        self.session = aiobotocore.get_session(loop=loop)
        self.bucket = 'openpacs'
        self.region = replica['location']

    @staticmethod
    def default_config():
        return {
            'location': 'eu-central-1',
        }

    def create_client(self):
        return self.session.create_client(
            's3',
            region_name=self.region,
            aws_secret_access_key=self.secret_access_key,
            aws_access_key_id=self.access_key_id,
        )

    async def init(self):
        async with self.create_client() as client:
            try:
                await client.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region,
                    },
                )
                await client.put_bucket_cors(
                    Bucket=self.bucket,
                    CORSConfiguration={
                        'CORSRules': [{
                            'AllowedHeaders': ['Authorization'],
                            'AllowedMethods': ['GET'],
                            'AllowedOrigins': ['*'],
                            'MaxAgeSeconds': 3600
                        }]
                    }
                )
            except Exception as e:
                if 'BucketAlreadyOwnedByYou' not in str(e):
                    raise

    async def index(self):
        async with self.create_client() as client:
            paginator = client.get_paginator('list_objects')
            async for result in paginator.paginate(Bucket=self.bucket):
                for c in result.get('Contents', []):
                    try:
                        patient_id, study_id, series_id, name = c['Key'].split('/')
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
                        'location': c['Key'],
                        'hash': c['ETag'].replace('"', ''),
                    }

    def get_key(self, filedata):
        return os.path.join(
            str(filedata['patient_id']),
            str(filedata['study_id']) or 'empty',
            str(filedata['series_number']) or 'empty',
            filedata['name'],
        )

    async def copy(self, src, filedata):
        key = self.get_key(filedata)

        if isinstance(src, SpooledTemporaryFile):
            src.seek(0)
            body = BytesIO(src.read())

        elif isinstance(src, str):
            body = open(src, 'rb')
        elif isinstance(src, BytesIO):
            body = src
        else:
            raise ValueError('Unsupported source')

        async with self.create_client() as client:
            resp = await client.put_object(
                Bucket=self.bucket, Key=key, Body=body,
            )
        return {
            'location': key
        }

    async def fetch(self, filedata):
        key = self.get_key(filedata)

        async with self.create_client() as client:
            response = await client.get_object(Bucket=self.bucket, Key=key)
            async with response['Body'] as stream:
                data = await stream.read()
                tmp_file = BytesIO(data)
            return tmp_file

    async def serve(self, filedata):
        # async with self.create_client() as client:
        #     response = client.generate_presigned_url(
        #         'get_object',
        #         Params={'Bucket': self.bucket, 'Key': filedata['location']}
        #     )
        # return RedirectResponse(url=response)
        fp = await self.fetch(filedata)
        return StreamingResponse(fp)

    async def delete(self, filedata):
        key = self.get_key(filedata)

        async with self.create_client() as client:
            await client.delete_object(Bucket=self.bucket, Key=key)
