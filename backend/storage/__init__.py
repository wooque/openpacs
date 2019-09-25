from storage.storage import Storage
from storage.local_storage import LocalStorage
from storage.s3 import S3Storage
from storage.b2 import B2Storage

Storage.register(LocalStorage)
Storage.register(S3Storage)
Storage.register(B2Storage)