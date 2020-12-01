from ddb import schemas
from ddb.schemas import Structure, SystemBase
from ddb import botodb
import uuid
from typing import List

table = botodb.BotoTable()


def only_alive(structures: List[dict]) -> List[schemas.Structure]:
    tmp_list = []
    for structure in structures:
        s = form_structure(structure)
        if s.structure_state != 'Dead':
            tmp_list.append(s)
    return tmp_list


def form_structure(structure: dict) -> Structure:
    pk = structure.pop('pk')
    sk = structure.pop('sk')
    return Structure(structure_id=pk, system_id=sk, **structure)


def get_structure(structure_id: str, system_id: str) -> Structure:
    schemas.validate_system(system_id)
    structure = table.get(structure_id, system_id)
    return form_structure(structure)


def get_structures(region: str, system: str = None):
    if not system:
        return only_alive(table.query_index('structure_index', {'region_id': region}))
    else:
        schemas.validate_system(system)
        structures = table.query_index('structure_index', {'region_id': region}, {'sk': system})
        return only_alive(structures)


def search_structures(structure: schemas.StructureCreate):
    if not structure.region_id:
        setattr(structure, 'region_id', get_region(structure.sk))
    system_structures = list(table.query_index('structure_index', {'region_id': structure.region_id},
                                               {'sk': structure.sk}))
    for system_structure in system_structures:
        s = form_structure(system_structure)
        if s.name in structure.name:
            return s
    return False


def create_structure(structure: schemas.StructureCreate):
    schemas.validate_system(structure.sk)
    if not structure.region_id:
        setattr(structure, 'region_id', str(get_region(structure.sk)))
    db_str = schemas.Structure(structure_id=str(uuid.uuid4()), system_id=structure.sk, **structure.dict())
    table.put(db_str)
    return db_str


def update_structure(structure_id: str, structure: schemas.StructureCreate):
    schemas.validate_system(structure.sk)
    current_structure = get_structure(structure_id, structure.sk)
    print(structure.dict())
    for k, v in structure.dict().items():
        print(f"checking {k}")
        curr = getattr(current_structure, k)
        new = getattr(structure, k)
        if (not new) and curr:
            setattr(structure, k, curr)
    print(structure.dict())
    new_structure = Structure(structure_id=structure_id, system_id=structure.sk, **structure.dict())
    table.put(new_structure)
    return new_structure


def create_system(system: schemas.SystemBase):
    table.put(system)
    return system


def get_region(system: str):
    results = table.query(system)
    print(results)
    for item in results:
        if item.get('is_system'):
            return item.get('sk')
    return False

