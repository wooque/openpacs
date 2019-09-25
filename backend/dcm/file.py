import pydicom


def clean(text, strict=False):
    ret = str(text).strip()
    if len(ret) and ret[0] == '\'':
        ret = ret[1:-1]
    if len(ret) and ret[0] == '"':
        ret = ret[1:-1]
    if strict:
        ret = ret.replace('/', '-')
    return ret


def get_meta(data):
    data_dict = dict(data)
    cleaned = dict((v.name, clean(v.repval)) for v in data_dict.values())
    ret = {
        'patient_id': clean(data.PatientID, strict=True),
        'patient_name': clean(getattr(data, 'PatientName', '')),
        'patient_birth_date': clean(getattr(data, 'PatientBirthDate', '')),
        'patient_sex': clean(getattr(data, 'PatientSex', '')),
        'study_id': clean(data.StudyID, strict=True),
        'study_description': clean(getattr(data, 'StudyDescription', '')),
        'series_number': clean(data.SeriesNumber, strict=True),
        'modality': clean(data.Modality),
        'series_description': clean(getattr(data, 'SeriesDescription', '')),
        'cleaned': cleaned,
        'raw': data_dict,
    }
    return ret


def parse_dcm(file):
    data = pydicom.dcmread(file, stop_before_pixels=True)
    return get_meta(data)
