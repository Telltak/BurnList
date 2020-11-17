from sqlalchemy.orm import Session

from sql_db import schemas, models


def get_structure(db: Session, structure_id: int):
    return db.query(models.Structure).filter(models.Structure.id == structure_id).first()


def get_structures(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Structure).offset(skip).limit(limit).all()


def get_structures_by_identifier(db: Session, identifier_type: str, identifier, skip: int = 0, limit: int = 100):
    return db.query(models.Structure).filter(getattr(models.Structure, identifier_type) == identifier).offset(skip) \
        .limit(limit).all()


def create_structure(db: Session, structure: schemas.StructureCreate):
    db_structure = models.Structure(**structure.dict())
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure


def update_structure(db: Session, structure: schemas.StructureCreate, structure_id: int):
    db.query(models.Structure).filter(models.Structure.id == structure_id).update(structure)
    db.commit()
    db_updated = db.query(models.Structure).filter(models.Structure.id == structure_id).first()
    return db_updated


def delete_structure(db: Session, structure_id: int):
    db_structure = db.query(models.Structure).filter(models.Structure.id == structure_id).first()
    db_structure.structurestate = "Dead"
    db.commit()
    return db_structure