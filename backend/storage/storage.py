class Storage:
    storage_types = {}
    storages = {}

    @staticmethod
    def register(cls):
        Storage.storage_types[cls.name] = cls

    @staticmethod
    def get_class(type_):
        return Storage.storage_types[type_]

    @staticmethod
    def default_config_by_type(type_):
        return Storage.get_class(type_).default_config()

    @staticmethod
    def default_config():
        return {}

    @staticmethod
    async def get(replica):
        rid = replica['id']

        if rid not in Storage.storages:
            cls = Storage.get_class(replica['type'])
            s = cls(replica)
            await s.init()
            Storage.storages[rid] = s

        return Storage.storages[rid]

    async def init(self):
        pass

    async def index(self):
        raise NotImplemented

    async def copy(self, src, file_data):
        raise NotImplemented

    async def fetch(self, file_data):
        raise NotImplemented

    async def serve(self, file_data):
        raise NotImplemented

    async def delete(self, file_data):
        raise NotImplemented
