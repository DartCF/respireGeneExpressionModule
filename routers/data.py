# %%
import pandas as pd
import tempfile
import zipfile
import boto3
import os
import re

from dotenv import load_dotenv
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import insert

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
    prefix="/v1/data",
    tags=['Data'],
    dependencies=[Depends(get_db)]
)

@router.post("/download", response_class=FileResponse)
def download_data_file(study_accessions: List[str], db: Session = Depends(get_db)):
    """Download selected studies

    Args:\n
        study_accessions (list[str]): A list of study IDs
        db (Session, optional): Database session. Defaults to Depends(get_db).

    Returns:\n
        FileResponse: A ZIP file containing data for selected studies
    """
    # get metadata for all selected studies
    metadta_query = db.query(
        models.Sample.sample_accession,
        models.Sample.variable,
        models.Sample.value
    ).filter(
        models.Sample.accession_number.in_(study_accessions)
    ).distinct()

    # read into memory
    res_df = pd.read_sql(
        metadta_query.statement, db.bind
    ).drop_duplicates(
        ['sample_accession', 'variable']
    ).pivot(
        index='sample_accession', columns='variable', values='value'
    ).reset_index()

    # stop if empty
    if res_df.shape[0] == 0:
        raise HTTPException(
            status_code=404, detail="Studies specified do not have data available for download")

    # read gene expression data
    data_query = db.query(
        models.GeneExpression.gene,
        models.GeneExpression.sample_accession,
        models.GeneExpression.value
    ).filter(
        models.GeneExpression.accession_number.in_(study_accessions)
    ).distinct()

    data_df = pd.read_sql(
        data_query.statement, db.bind
    ).pivot(
        index='gene', columns='sample_accession', values='value'
    ).reset_index()

    outdir = os.path.join(tempfile.gettempdir(), 'respire_data_download')

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    zip_fp = os.path.join(outdir, 'respire_data_download.zip')
    metadata_fp = os.path.join(outdir, "metadata.csv")
    data_fp = os.path.join(outdir, "data_compendium.csv")
    readme_fp = os.path.join(outdir, "readme.txt")

    res_df.to_csv(metadata_fp, index=False)
    data_df.to_csv(data_fp, index=False)

    archive_time = datetime.now()

    with open(readme_fp, 'wt') as f:
        f.writelines(line + "\n" for line in [f"Downloaded on {archive_time.strftime('%m-%d-%Y at %H:%M:%S')}",
                                              "Metadata sourced from NCBI databases including BioProject and the Gene Expression Omnibus",
                                              "Includes data from the following studies:", "  " + "\n  ".join(study_accessions)])

    file_list = [metadata_fp, data_fp, readme_fp]

    with zipfile.ZipFile(zip_fp, 'w') as zip:
        for file in file_list:
            zip.write(file,
                      compress_type=zipfile.ZIP_DEFLATED,
                      arcname=f"respire_data_download_{archive_time.strftime('%Y%m%d_%H_%M_%S')}/{os.path.basename(file)}")

    headers = {'Content-Disposition': 'attachment; filename="respire_data_download.zip"',
               'Accept': 'application/zip, application/octet-stream '}

    return FileResponse(zip_fp, headers=headers)
