from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse

from api.utils import get_id
from db.conn import get_conn
from db.patient import Patient


async def get_patient_by_id(request):
    patient_id = get_id(request)
    async with get_conn() as conn:
        return await Patient(conn).get_extra(patient_id)


class PatientHandler(HTTPEndpoint):
    async def get(self, request):
        data = await get_patient_by_id(request)
        if not data:
            return UJSONResponse(status_code=404)
        return UJSONResponse(data)
