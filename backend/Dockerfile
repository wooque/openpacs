FROM python:3.7.4-alpine

RUN apk add gcc musl-dev make && pip3 install \
aiobotocore==0.10.3 \
aiofiles==0.4.0 \
asyncpg==0.18.3 \
b2sdk==1.0.0rc1 \
gunicorn==19.9.0 \
elasticsearch-async==6.2.0 \
email-validator==1.0.4 \
pydicom==1.3.0 \
pynetdicom==1.4.1 \
PyJWT==1.7.1 \
PyPika==0.35.2 \
PyYAML==5.1.2 \
python-dateutil==2.8.0 \
python-multipart==0.0.5 \
starlette==0.12.8 \
ujson==1.35 \
uvicorn==0.8.6 \
&& apk del gcc musl-dev make

ADD ./ /openpacs

WORKDIR /openpacs

ENV OPENPACS_DOCKER=true

CMD ./start.sh
