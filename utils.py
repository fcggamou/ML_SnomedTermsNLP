import os
import boto3
import zipfile
import pickle
import json
import nlp_utils
from config import models_path, S3_bucket
from pathlib import Path
from spacy.tokens import Doc
from snomed import Snomed
from datetime import datetime
import dateutil


def download_file_from_S3(file: str, dest_dir: str = models_path, force: bool = True) -> str:
    dest_path = os.path.join(Path(dest_dir), f'{file}')
    if force and os.path.isfile(dest_path):
        os.remove(dest_path)
    if not os.path.isfile(dest_path):
        print('Downloading {} from S3'.format(file))
        makedir_if_not_exists(dest_dir)
        s3 = boto3.client('s3')
        s3.download_file(S3_bucket, 'Models/' + file, dest_path)

    return dest_path


def unzip_file(filename: str, dest: str):
    print(f'Unzipping {filename}')
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(dest)


def makedir_if_not_exists(dest):
    if not os.path.exists(dest):
        os.makedirs(dest)


def load_from_file(filename):
    with open(filename, "rb") as f:
        unpickler = pickle.Unpickler(f)
        data = unpickler.load()
    return data


def dump_to_file(object, filename):
    with open(filename, 'wb') as f:
        pickle.dump(object, f, protocol=pickle.HIGHEST_PROTOCOL)


def overlap(e1, e2):
    """ Returns true if the intervals e1 and e2 overlap """
    start1, end1 = e1[0], e1[1]
    start2, end2 = e2[0], e2[1]
    return start1 >= start2 and end1 <= end2 or\
        start1 >= start2 and start1 < end2 or\
        start2 >= start1 and end2 <= end1 or\
        start2 >= start1 and start2 < end1


def doc_to_json(doc: Doc, original_text: str) -> str:
    termsList = []

    for ent, cats in zip(doc.ents, doc.cats):
        qualifiers = []
        qualifierCode = None
        snomed_term = Snomed.instance().search_by_code(ent.label_)
        if doc.cats is not None and len(doc.cats) > 0:
            qualifierCode = nlp_utils.get_max_cat(cats)
            if qualifierCode is not None and qualifierCode != 'None':
                qualifier = {
                    'SNOMED-CT Code': qualifierCode,
                    'SNOMED-CT Description': Snomed.instance().search_by_code(qualifierCode).description
                }
                qualifiers.append(qualifier)
        term = {
            'Text': ent.text,
            'SNOMED-CT Code': ent.label_,
            'SNOMED-CT Description': snomed_term.description,
            'SNOMED-CT Domain': snomed_term.domain,
            'Qualifiers': qualifiers
        }
        termsList.append(term)
    ehrTextDic = {
        "Processed Text": original_text,
        "Terms Found": termsList
    }
    json_data = json.dumps(ehrTextDic, indent=4, ensure_ascii=False)
    print(json_data)
    return json_data


def json_date_to_datetime(json_date: str) -> datetime:
    return dateutil.parser.parse(json_date, ignoretz=True)


def datetime_to_sql(date: datetime) -> str:
    return date.strftime('%Y-%m-%d %H:%M:%S')


def json_date_to_sql(json_date: str) -> str:
    return datetime_to_sql(json_date_to_datetime(json_date))


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
