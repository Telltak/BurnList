from typing import List, Optional

# FROM https://medium.com/data-rebels/fastapi-authentication-revisited-enabling-api-key-authentication-122dc5975680
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from ddb import schemas, crud, NotFoundException

import utils

API_KEY = "G777L3zdZ8"
API_KEY_NAME = "access_token"
COOKIE_DOMAIN = "localtest.me"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

app = FastAPI()


# TODO make this real auth
async def get_api_key(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie)
):
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
try:
    if not crud.table.get('systems_imported', 'true'):
        utils.create_systems()
except NotFoundException:
    utils.create_systems()


# TODO set up auth middlewear


@app.get('/structures/{structure_id}', response_model=schemas.Structure)
def get_structure(structure_id: str, system_id: str):
    schemas.validate_system(system_id)
    db_structure = crud.get_structure(structure_id, system_id)
    return db_structure


@app.get('/structures/region/{region}', response_model=List[schemas.Structure])
def get_region_structures(region: str):
    return crud.get_structures(region)


@app.get('/structures/system/{system}', response_model=List[schemas.Structure])
def get_system_structures(system: str):
    print(f"getting region for {system}")
    region = crud.get_region(system)
    print(f"got region {region}")
    return crud.get_structures(region, system)


@app.post('/structures/', response_model=schemas.Structure)
def create_structure(structure: schemas.StructureCreate):
    print(f"searching for structure in {structure.sk} with the name {structure.name}")
    db_structure = crud.search_structures(structure)
    print(db_structure)
    if db_structure:
        raise HTTPException(status_code=400, detail="Structure already registered")
    return crud.create_structure(structure=structure)


@app.put('/structures/{structure_id}', response_model=schemas.Structure)
def update_structure(structure_id: str, structure: schemas.StructureCreate):
    db_structure=crud.get_structure(structure_id, structure.sk)
    if not db_structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    print("gothere")
    return crud.update_structure(structure_id, structure)


@app.delete("/structures/{structure_id}", response_model=schemas.Structure)
def delete_structure(structure_id: str, system_id: str):
    db_structure = crud.get_structure(structure_id, system_id)
    if not db_structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    setattr(db_structure, 'structure_state', 'Dead')
    return crud.update_structure(structure_id, db_structure)
