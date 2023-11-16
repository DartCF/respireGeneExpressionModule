from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from . import models, schemas

# return results from front end search


def search_studies(db: Session,
                   search_string: str,
                   n_samples: int,
                   organism: str,
                   profiling_method: str,
                   has_data: int):
    return db.query(
        models.Study
    ).filter(
        models.Study.description.ilike(f"%{search_string}%"),
        models.Study.n_samples >= n_samples,
        models.Study.organism_name == organism,
        models.Study.gds_type == profiling_method,
        models.Study.has_data == has_data
    ).all()


def add_studies(db: Session, studies: List[schemas.StudyCreate]):
    '''
    Add one or more studies to the study metadata
    '''
    for study in studies:
        s = models.Study(**study.dict())
        db.add(s)
    db.commit()
    return [s.study_id for s in studies]


def list_organisms(db: Session, has_data: int = 1):
    '''
    Get a list of the available organisms in the database
    '''
    stmt = select(
        models.Study.organism_name.distinct()
    ).filter(
        models.Study.has_data == has_data
    ).order_by(
        models.Study.organism_name
    )

    res = db.execute(stmt).all()

    return [str(i[0]) for i in res]


def list_profiling_methods(db: Session, has_data: int = 1):
    '''
    Get a list of the available organisms in the database
    '''
    stmt = select(
        models.Study.gds_type.distinct()
    ).filter(
        models.Study.has_data == has_data
    ).order_by(
        models.Study.gds_type
    )

    res = db.execute(stmt).all()

    return [str(i[0]) for i in res]


def get_study_accessions(db: Session):
    '''
    Get a list of all study accessions
    '''
    stmt = select(
        models.Study.accession_number.distinct()
    )

    res = db.execute(stmt).all()

    return [str(i[0]) for i in res]


