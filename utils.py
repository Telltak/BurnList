import requests
import tempfile
import bz2
import csv
from ddb import crud, schemas

SDE_BASE = 'https://www.fuzzwork.co.uk/dump/latest/'
SOLARSYSTEMS_URL = f'{SDE_BASE}mapSolarSystems.csv.bz2'


def download_sde(url):
    with tempfile.TemporaryFile() as tmp:
        tmp.write(requests.get(url).content)
        tmp.seek(0)

        with bz2.BZ2File(tmp, 'r') as uncompressed:
            data = uncompressed.read().decode('ascii')

    with tempfile.TemporaryFile(mode='w+t') as tmp:
        tmp.write(data)
        tmp.seek(0)

        for x in csv.DictReader(tmp):
            yield x


def create_systems():
    print("creating systems")
    system_data = download_sde(SOLARSYSTEMS_URL)

    table = crud.table

    for system in system_data:
        crud.create_system(schemas.SystemBase(pk=system['solarSystemID'], sk=system['regionID']))

    table.put(schemas.SystemBase(pk='systems_imported', sk='true'))
