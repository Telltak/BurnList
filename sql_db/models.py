from sqlalchemy import Column, Integer, String

from .database import Base


# TODO make this all alembic

class Structure(Base):
    __tablename__ = "structures"

    id = Column(Integer, primary_key=True, index=True)
    system = Column(String)
    name = Column(String)
    corp = Column(String, default=None)
    alliance = Column(String, default=None)
    structurestate = Column(Integer, default=0)
    structuretype = Column(String, default=None)
    fitting = Column(String, default=None)
