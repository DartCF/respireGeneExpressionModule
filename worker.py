# %%
from db_utils import models
from db_utils.database import SessionLocal

from source_data.metadata_parser import MetadataParser
from source_data.functions import get_sample_metadata

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import insert, select, create_engine

from os.path import join, dirname
from dotenv import load_dotenv
from celery import Celery, Task
from io import StringIO, TextIOWrapper

import os
import boto3
import csv

# %%
dotenv_path = join(dirname(__file__), 'db_utils', '.env')
load_dotenv(dotenv_path)

#########################
# HELPERS
#########################

# create a task with a database session available


class DatabaseTask(Task):
    _db = None

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db


#########################
# celery config
#########################
redis_pass = os.environ.get("REDIS_AUTH")

if redis_pass is None:
    celery_broker_url, celery_result_backend = "redis://redis:6379/0", "redis://redis:6379/0"
else:
    celery_broker_url, celery_result_backend = f"redis://:{redis_pass}@redis:6379/0", f"redis://:{redis_pass}@redis:6379/0"

celery = Celery(__name__)

celery.conf.broker_url = celery_broker_url
celery.conf.result_backend = celery_result_backend

#########################
# tasks
#########################


@celery.task(base=DatabaseTask, bind=True, name="add_gene_expression_data")
def ingest_gene_expression_data(self, aws_file_name: str):

    # create a client
    s3_client = boto3.client("s3",
                             region_name='us-east-2',
                             aws_access_key_id=os.environ.get(
                                 "AWS_ACCESS_KEY_ID"),
                             aws_secret_access_key=os.environ.get(
                                 "AWS_SECRET_ACCESS_KEY")
                             )
    # get a file response
    response = s3_client.get_object(
        Bucket=os.environ.get('AWS_BUCKET'), Key=aws_file_name)

    engine = create_engine(os.environ.get('SQLALCHEMY_DATABASE_URL'))

    # number of records to process at a time
    batch_size = 250000

    csv_reader = csv.DictReader(
        TextIOWrapper(
            response['Body'], encoding='utf-8'
        )
    )

    batch = []
    for i, row in enumerate(csv_reader):

        batch.append(row)

        if len(batch) == batch_size:
            engine.execute(
                insert(models.GeneExpression,
                       batch
                       )
            )
            batch = []
    # insert the last batch (needed if leftover < batch_size)
    if len(batch) > 0:
        engine.execute(
            insert(models.GeneExpression,
                   batch
                   )
        )

    populate_has_data_cmd = """
    update studies set has_data = 1 
    where external_db_id in (select distinct study_accession from gene_expression)
    """

    engine.execute(populate_has_data_cmd)

    return {'status': True}


@celery.task(base=DatabaseTask, bind=True, name="add_metadata")
def ingest_gene_expression_metadata(self, query):
    """Add gene expression data to 

    Args:
        gene_expressions (_type_): _description_

    Returns:
        _type_: _description_
    """
    parser = MetadataParser(entrez_email=query['entrez_email'],
                            bioproject_query=query['bioproject_query'])

    parser.fetch_results().parse_search_results().link_bioproject_studies()

    with self.db.bind.begin() as conn:
        conn.execute(
            insert(models.Study),
            parser.export_study_metadata()
        )

    return {'status': True}


@celery.task(base=DatabaseTask, bind=True, name="add_sample_metadata")
def ingest_gene_expression_sample_metadata(self):
    """Add gene expression data to 

    Args:
        gene_expressions (_type_): _description_

    Returns:
        _type_: _description_
    """

    stmt = select(
        models.Study.external_db_id
    ).filter(
        models.Study.external_db_id.isnot(None)
    )
    res = self.db.execute(stmt).all()
    gse_ids = [str(i[0]) for i in res]

    if len(gse_ids) == 0:
        return JSONResponse({'message': "No GSE IDs found in the database. Ingest study metadata to continue"
                             }, status_code=status.HTTP_428_PRECONDITION_REQUIRED)

    print("getting sample metadata")
    sample_meta = get_sample_metadata(gse_ids)

    print("starting")
    engine = create_engine(os.environ.get('SQLALCHEMY_DATABASE_URL'))
    for i, meta in enumerate(sample_meta):
        print(f"Inserting batch {i}")
        engine.execute(
            insert(
                models.Sample,
                meta
            )
        )

    return {'status': True}
