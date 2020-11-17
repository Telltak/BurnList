from typing import List

# FROM https://medium.com/data-rebels/fastapi-authentication-revisited-enabling-api-key-authentication-122dc5975680
from fastapi import Security, Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey

from starlette.status import HTTP_403_FORBIDDEN

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


from sql_db import schemas, models, crud
from sql_db.database import SessionLocal, engine
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/structures/", response_model=List[schemas.Structure])
def get_all_structures(api_key: APIKey = Depends(get_api_key), skip: int = 0, limit: int = 100,
                       db: Session = Depends(get_db)):
    for k, v in schemas.Structure.__fields__.items():
        print(f"key: {k}, value: {v.type_}")
    structures = crud.get_structures(db, skip=skip, limit=limit)
    return structures


@app.get("/structures/{structure_id}", response_model=schemas.Structure)
def get_structure(structure_id: int, api_key: APIKey = Depends(get_api_key), db: Session = Depends(get_db)):
    db_structure = crud.get_structure(db, structure_id)
    if db_structure is None:
        raise HTTPException(status_code=404, detail="Structure not found")
    return db_structure


@app.get("/structures/alliance/{alliance}", response_model=List[schemas.Structure])
def get_structure_by_alliance(alliance: str, api_key: APIKey = Depends(get_api_key), skip: int = 0, limit: int = 100,
                              db: Session = Depends(get_db)):
    db_structures = crud.get_structures_by_identifier(db, 'alliance', alliance, skip=skip, limit=limit)
    return db_structures


@app.get("/structures/corporation/{corp}", response_model=List[schemas.Structure])
def get_structure_by_corp(corp: str, api_key: APIKey = Depends(get_api_key), skip: int = 0, limit: int = 100,
                          db: Session = Depends(get_db)):
    db_structures = crud.get_structures_by_identifier(db, 'corp', corp, skip=skip, limit=limit)
    return db_structures


@app.get("/structures/state/{state}", response_model=List[schemas.Structure])
def get_structure_by_state(state: schemas.StructureState, api_key: APIKey = Depends(get_api_key), skip: int = 0,
                           limit: int = 100,
                           db: Session = Depends(get_db)):
    db_structures = crud.get_structures_by_identifier(db, 'structurestate', state, skip=skip, limit=limit)
    return db_structures


@app.get("/structures/name/{name}", response_model=List[schemas.Structure])
def get_structure_by_name(name: str, api_key: APIKey = Depends(get_api_key), skip: int = 0, limit: int = 100,
                          db: Session = Depends(get_db)):
    db_structures = crud.get_structures_by_identifier(db, 'name', name, skip=skip, limit=limit)
    return db_structures


@app.get("/structures/type/{structuretype}", response_model=List[schemas.Structure])
def get_structure_by_type(structuretype: schemas.StructureType, api_key: APIKey = Depends(get_api_key), skip: int = 0,
                          limit: int = 100, db: Session = Depends(get_db)):
    db_structures = crud.get_structures_by_identifier(db, 'structuretype', structuretype, skip=skip, limit=limit)
    return db_structures


@app.post("/structures/", response_model=schemas.Structure)
def create_structure(structure: schemas.StructureCreate, db: Session = Depends(get_db),
                     api_key: APIKey = Depends(get_api_key)):
    db_structure = crud.get_structures_by_identifier(db, identifier=structure.name, identifier_type='name')
    if db_structure:
        raise HTTPException(status_code=400, detail="Structure already registered")
    return crud.create_structure(db=db, structure=structure)


@app.put("/structures/{structure_id}", response_model=schemas.Structure)
def update_structure(structure_id: int, structure: schemas.StructureCreate, db: Session = Depends(get_db),
                     api_key: APIKey = Depends(get_api_key)):
    db_structure = crud.get_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return crud.update_structure(db=db, structure=structure, structure_id=structure_id)


@app.delete("/structures/{structure_id}", response_model=schemas.Structure)
def kill_structure(structure_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    db_structure = crud.get_structure(db, structure_id)
    if not db_structure:
        raise HTTPException(status_code=404, detail="Structure not found")
    return crud.delete_structure(db=db, structure_id=structure_id)
