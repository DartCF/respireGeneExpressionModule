# %%
import pandas as pd
import os

from dotenv import load_dotenv
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse

from sqlalchemy.orm import Session

from db_utils.database import get_db
from db_utils import schemas, models
from worker import *

# %%

# create path to db_utils (parent directory of this file, the db_utils/.env)
dotenv_path = os.path.join(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), os.pardir)
    ), 'db_utils', '.env')
load_dotenv(dotenv_path)


router = APIRouter(
    prefix="/v1/admin",
    tags=['Data'],
    dependencies=[Depends(get_db)]
)


@router.get('/dataStructure', status_code=200, response_model=schemas.Admin)
def get_data_structure(db: Session = Depends(get_db)):
    # create a dictionary that conforms to the admin schema from schemas.py
    data_structure = {
        'study_metadata_table': {
            'db_schema': 'public',
            'table': 'studies',
            # create fields, a list of dictionaries matching the StudyBase schema from schemas.py
            'fields': [{'study_id': 'integer'},
                       {"title": "character"},
                       {"description": "character"},
                       {"data_type": "character"},
                       {"submitted": "character"},
                       {"organism_name": "character"},
                       {"organism_id": "integer"},
                       {"external_db": "character"},
                       {"external_db_id": "character"},
                       {"organization": "character"},
                       {"accession_number": "character"},
                       {"n_samples": "integer"},
                       {"gds_type": "character"},
                       {"has_data": "integer"}]
        },
        'sample_metadata_table': {
            'db_schema': 'public',
            'table': 'samples',
            'fields': [{'id': 'integer'},
                       {'accession_number': 'character'},
                       {'sample_accession': 'character'},
                       {'variable': 'character'},
                       {'value': 'character'}]
        },
                       
        'data_table': {
            'db_schema': 'public',
            'table': 'gene_expression',
            # create fields, a list of dictionaries matching the GeneExpression model in models.py
            'fields': [{'accession_number': 'character'},
                       {'gene': 'character'},
                       {'sample_accession': 'character'},
                       {'value': 'character'}]
        },
        'shared_key': 'accession_number'
    }
    return JSONResponse(data_structure, status_code=200)

# create a route that returns a InputCollection schema with two Test schema objects inside


@router.get('/inputs', status_code=200, response_model=schemas.InputCollection)
def get_test():
    input_collection = {
        'inputs': [
            {
                'function': "checkboxInput",
                'searchField': "has_data",
                'split_download': False,
                'args': {
                    'label': "Has data?",
                    'checked': True
                }
            },
            {
                'function': "textInput",
                'searchField': "search_string",
                'split_download': False,
                'args': {
                    'label': "Search terms",
                    'placeholderText': "Enter one or more search terms"
                }
            },
            {
                'function': "selectInput",
                'searchField': "organism",
                'split_download': True,
                'args': {
                    'label': "Select organism",
                    'options': [],
                    # 'source': 'http://localhost:8000/v1/studies/naiveOrganisms'
                    'source': 'https://respire.dartmouth.edu/v1/studies/naiveOrganisms'
                }
            },
            {
                'function': "selectInput",
                'searchField': "profiling_method",
                'split_download': True,
                'args': {
                    'label': "Select data profiling method",
                    'options': [],
                    # 'source': 'http://localhost:8000/v1/studies/naiveProfilingMethod'
                    'source': 'https://respire.dartmouth.edu/v1/studies/naiveProfilingMethod'
                }
            },
            {
                'function': "numberInput",
                'searchField': "n_samples",
                'split_download': False,
                'args': {
                    'label': "Minimum Samples",
                    'defaultValue': 50
                }
            }
        ]
    }
    return JSONResponse(input_collection, status_code=200)
