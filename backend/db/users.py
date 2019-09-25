import binascii
import hashlib
import random
import string

from config import config
from exeptions import ApiException
from db.table import Table


def rand_pwswd(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def pswd_hash(pswd):
    data = hashlib.pbkdf2_hmac('sha256', pswd.encode('utf8'), b'', 10000)
    return binascii.hexlify(data).decode('utf8')


class Users(Table):
    name = 'users'

    async def sync_db(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username CITEXT NOT NULL,
            password TEXT NOT NULL,
            admin BOOLEAN NOT NULL DEFAULT FALSE,
            status TEXT NOT NULL DEFAULT 'active',
            created TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
            updated TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc')
        );
        """)
        await self.exec("""
        CREATE INDEX IF NOT EXISTS users_username on users(username);
        """)

    @staticmethod
    def to_json(data):
        return dict(data)

    async def login(self, username, password):
        q = self.select('*').where(self.table.username == username)
        data = await self.fetchone(q)
        if not data:
            raise ApiException('User does not exists')
        if pswd_hash(password) != data['password']:
            raise ApiException('Password is not correct')
        if data['status'] != 'active':
            raise ApiException('User deactivated')
        return data

    async def add_superadmin(self):
        q = self.select('*').where(self.table.username == 'admin')
        data = await self.fetchone(q)
        if not data:
            pswd = pswd_hash(config['superadmin_pass'])
            q = self.insert().columns('username', 'password', 'admin').insert('admin', pswd, True)
            await self.exec(q)

    async def change_password(self, user, password):
        pswd = pswd_hash(password)
        q = self.update().where(self.table.id == user.id).set(self.table.password, pswd)
        await self.exec(q)

    async def add_user(self, username, is_admin):
        pswd = rand_pwswd()
        ph = pswd_hash(pswd)
        q = self.insert().columns('username', 'password', 'admin').insert(username, ph, is_admin)
        await self.exec(q)
        return {'password': pswd}

    async def get_users(self, offset=None, limit=None, username=None):
        if offset is None:
            offset = 0
        if limit is None:
            limit = 20
        q = self.select('id', 'username', 'admin', 'created', 'status')
        if username:
            q = q.where(self.table.username.ilike('%' + username + '%'))
        q = q.orderby('username').offset(offset).limit(limit)
        return await self.fetch(q)

    async def deactivate(self, user_id):
        q = self.update().where(self.table.id == user_id).set(self.table.status, 'deactivated')
        await self.exec(q)

    async def new_pswd(self, user_id):
        pswd = rand_pwswd()
        ph = pswd_hash(pswd)
        q = self.update().where(self.table.id == user_id).set(self.table.password, ph)
        await self.exec(q)
        return pswd

    async def is_active(self, user_id):
        q = self.select('status').where(self.table.id == user_id)
        status = await self.fetchval(q)
        return status == 'active'
