from typing import Optional, Dict, List, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel

# study schemata
class StudyBase(BaseModel):
    study_id: int
    title: str
    description: str
    data_type: str
    submitted: Optional[str]
    organism_name: str
    organism_id: int
    external_db: str
    external_db_id: str
    organization: Optional[str]
    accession_number: str
    n_samples: int
    gds_type: Optional[str]
    has_data: int


class StudyCreate(StudyBase):
    pass

class Study(StudyBase):
    study_id: int
    class Config:
        orm_mode = True

# sample schemata

class SampleBase(BaseModel):
    sample_accession: str
    study_id: int
    sample_title: str

class SampleCreate(SampleBase):
    pass

class Sample(SampleBase):
    sample_accession: str
    study_id: int
    sample_title: str

    class Config:
        orm_mode = True

# search schema

class Search(BaseModel):
    search_string: str
    n_samples: int
    organism: str
    profiling_method: str
    has_data: int

# task status

class QueuedForUpload(BaseModel):
    task_id: str
    n_records: int

class Status(BaseModel):
    task_id: str
    task_status: str
    task_result: str

# gene expression schema

class GeneExpressionBase(BaseModel):
    accession_number: str
    gene: str
    sample_accession: str
    value: float

class GeneExpressionCreate(GeneExpressionBase):
    pass

class GeneExpression(GeneExpressionBase):
    accession_number: str
    gene: str
    sample_accession: str
    value: float

    class Config:
        orm_mode = True

class BioprojectQuery(BaseModel):
    entrez_email: str
    bioproject_query: str

# administrative schemata

class MetadataTable(TypedDict):
    db_schema: str
    table: str
    fields: List[Dict[str, str]]

class SampleMetadataTable(TypedDict):
    db_schema: str
    table: str
    fields: List[Dict[str, str]]

class DataTable(TypedDict):
    db_schema: str
    table: str
    fields: List[Dict[str, str]]

class Admin(BaseModel):
    metadata_table: MetadataTable
    sample_metadata_table: Optional[SampleMetadataTable]
    data_table: DataTable
    shared_key: str
    
class InputCollection(BaseModel):
    test_cases: List[dict]