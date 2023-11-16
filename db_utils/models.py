from sqlalchemy import Column, Integer, String

from .database import Base

class Study(Base):

    __tablename__ = "studies"

    study_id = Column(Integer, primary_key = True, unique = True, index = True)
    title = Column(String, default="")
    access  = Column(String, default="")
    description = Column(String, default="")
    data_type = Column(String)
    submitted = Column(String, default=None)
    organism_name = Column(String)
    organism_id = Column(Integer)
    external_db = Column(String)
    external_db_id = Column(String)
    organization = Column(String)
    accession_number = Column(String)
    n_samples = Column(Integer)
    gds_type = Column(String, default=None)
    has_data = Column(Integer, default=0)

class Sample(Base):

    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    accession_number = Column(String)
    sample_accession = Column(String)
    variable = Column(String)
    value = Column(String, default = "")

class GeneExpression(Base):

    __tablename__ = "gene_expression"

    accession_number = Column(String, primary_key=True)
    gene = Column(String, primary_key=True)
    sample_accession = Column(String, primary_key=True)
    value = Column(String)

    