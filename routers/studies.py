from fastapi import APIRouter, Depends
from typing import List
from db_utils.database import get_db
from db_utils import schemas, crud
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/v1/studies",
    tags=['Studies'],
    dependencies=[Depends(get_db)]
)

@router.post("/organisms", response_model=List[str])
def get_organisms(has_data: int, db: Session = Depends(get_db)):
    """Retrieve list of all organisms in the database

    Args:\n
        db (Session, optional): A database session. Defaults to Depends(get_db).

    Returns:\n
        list[str]: A list of organism names
    """

    return crud.list_organisms(db=db, has_data=has_data)

@router.get("/naiveOrganisms", response_model=List[str])
def get_organisms(db: Session = Depends(get_db)):
    """Retrieve list of all organisms in the database

    Args:\n
        db (Session, optional): A database session. Defaults to Depends(get_db).

    Returns:\n
        list[str]: A list of organism names
    """

    return crud.list_organisms(db=db, has_data=1)

@router.post("/profilingMethod", response_model=List[str])
def get_profiling_methods(has_data: int, db: Session = Depends(get_db)):
    """Retrieve list of all profiling methods

    Args:\n
        db (Session, optional): A database session. Defaults to Depends(get_db).

    Returns:\n
        list[str]: A list of profiling methods
    """

    return crud.list_profiling_methods(db=db, has_data=has_data)

@router.get("/naiveProfilingMethod", response_model=List[str])
def get_profiling_methods(db: Session = Depends(get_db)):
    """Retrieve list of all profiling methods

    Args:\n
        db (Session, optional): A database session. Defaults to Depends(get_db).

    Returns:\n
        list[str]: A list of profiling methods
    """

    return crud.list_profiling_methods(db=db, has_data=1)


@router.post("/searchMetadata", response_model=List[schemas.Study])
def find_studies(Search: schemas.Search, db: Session = Depends(get_db)):
    """Search project metadata for results

    Args:\n
        Search (schemas.Search): A valid search object\n
        db (Session, optional): A database session. Defaults to Depends(get_db).

    Returns:\n
        list[schemas.Study]: List of studies
    """
    return crud.search_studies(db=db,
                               search_string=Search.search_string,
                               organism=Search.organism,
                               n_samples=Search.n_samples,
                               profiling_method=Search.profiling_method,
                               has_data=Search.has_data
                               )
