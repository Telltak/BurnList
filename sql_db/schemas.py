from typing import Optional
from enum import Enum

from pydantic import BaseModel, AnyHttpUrl


class StructureState(str, Enum):
    full = "Shield"
    armor = "Armor"
    hull = "Hull"
    dead = "Dead"


class StructureType(str, Enum):
    ansiblex = "Ansiblex"
    astrahus = "Astrahus"
    athanor = "Athanor"
    azbel = "Azbel"
    draccous = "Draccous"
    fortizar = "Fortizar"
    horizon = "Horizon"
    keepstar = "Keepstar"
    marginis = "Marginis"
    moreau = "Moreau"
    pharolux = "Pharolux"
    pos = "POS"
    prometheus = "Prometheus"
    raitaru = "Raitaru"
    sotiyo = "Sotiyo"
    tatara = "Tatara"
    tenebrex = "Tenebrex"


class StructureBase(BaseModel):
    system: str
    name: str
    corp: Optional[str] = None
    alliance: Optional[str] = None
    structurestate: Optional[StructureState] = "Shield"
    structuretype: StructureType
    fitting: Optional[AnyHttpUrl] = "https://evepraisal.com"


class StructureCreate(StructureBase):
    pass


class Structure(StructureBase):
    id: int

    class Config:
        orm_mode = True
