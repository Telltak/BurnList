from typing import Optional

from pydantic import BaseModel, AnyHttpUrl, validator, Field


STRUCTURE_STATES = ['Shield', 'Armor', 'Hull', 'Dead']

STRUCTURE_TYPES = ['Ansiblex', 'Astrahus', 'Athanor', 'Azbel', 'Draccous', 'Fortizar', 'Horizon', 'Keepstar',
                   'Marginis', 'Moreau', 'Pharolux', 'POS', 'Prometheus', 'Raitaru', 'Tatara', 'Tenebrex']


def resolve_location_type_enum(location_id):
    """Resolve the location item ID to its type name."""

    if 30000000 <= location_id <= 39999999:
        return "solar_system"
    if 60000000 <= location_id < 64000000:
        return "station"
    if location_id >= 100000000:
        return "item"

    return "other"


def validate_structure_state(structure_state: str):
    if structure_state not in STRUCTURE_STATES:
        raise ValueError(f"{structure_state} must be one of {STRUCTURE_STATES}")
    return structure_state


def validate_structure_type(structure_type: str):
    if structure_type not in STRUCTURE_TYPES:
        raise ValueError(f"{structure_type} must be one of {STRUCTURE_TYPES}")
    return structure_type


def validate_system(system_id: str):
    if not resolve_location_type_enum(int(system_id)) == "solar_system":
        raise ValueError(f"{system_id} must be a solar system ID - {resolve_location_type_enum(int(system_id))}")
    return system_id


class StructureBase(BaseModel):
    sk: str = Field(..., alias="system_id")
    region_id: Optional[str]
    name: str
    corp: Optional[str]
    alliance: Optional[str]
    structure_state: Optional[str]
    structure_type: Optional[str]
    fitting: Optional[AnyHttpUrl]
    fitting_type: Optional[str]

    @validator('structure_state')
    def correct_structure_state(cls, v):
        return validate_structure_state(v)

    @validator('structure_type')
    def correct_structure_type(cls, v):
        return validate_structure_type(v)

    @validator('sk')
    def correct_system(cls, v):
        return validate_system(v)


class StructureCreate(StructureBase):
    pass


class Structure(StructureBase):
    pk: str = Field(..., alias="structure_id")

    class Config:
        orm_mode = True


class SystemBase(BaseModel):
    pk: str
    sk: str
    is_system: bool = True
