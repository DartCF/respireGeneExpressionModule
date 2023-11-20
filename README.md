# Gene Expression API

The Gene Expression API is the central tool for managing gene expression data through RESPIRE. It provides methods for collecting study metadata from the National Center for Biotechnology Information (NCBI) as well as core functionality required by the RESPIRE frontend application.

# Technical Documentation 

This API uses the following technology stack:

* FastAPI (Python) -- API interface and functionality
* Postgres -- database


## About FastAPI

[FastAPI](https://fastapi.tiangolo.com/#:~:text=FastAPI%20is%20a%20modern%2C%20fast,the%20fastest%20Python%20frameworks%20available.) is a web framework for building APIs with Python based on standard Python type hints. It takes advantage of the [pydantic](https://docs.pydantic.dev/) library to enforce data type matching and features automatic OpenAPI documentation. You can 

## Gene Expression Study Metadata

Study metadata for the gene expression module comes from two databases under the umbrella of the NCBI.

### BioProject
A BioProject is a collection of biological data related to a single initiative, originating from a single organization or from a consortium. BioProject records represent a significant portion of the available metadata on the study level.
 
This implementation of the RESPIRE gene expression module is driven by a BioProject query provided to the `/v1/data/addGeneExpressionMetadata` route. All handling for downloading and linking is done by the `MetadataParser` class defined in `source_data/metadta_parser.py`.
 
The following sample query would source metadata for project with a project data type corresponding to either 'transcriptome' or 'gene expression' with the phrase "idiopathic pulmonary fibrosis" in the project description
  ```
  '"transcriptome or gene expression"[Project Data Type] AND "idiopathic pulmonary fibrosis"[Description]'
  ```

### Gene Expression Omnibus (GEO)

 GEO provides important supplementary study metadata, including the number of available samples. Studies in the BioProject database are linked to GEO using an external database ID.  

## Gene Expression Sample Metadata

The sample metadata for the gene expression module is parsed from files stored on the [NCBI FTP site](https://ftp.ncbi.nlm.nih.gov/geo/series). There is substantial variation in the available metadata for gene expression samples,so the metadata is normalized for storage

# Setup

To inititiate a new instance of the gene expression data module, you will need to create a secrets file in `db_utils`. Follow the template in `db_utils/.env_template`. For local development, this can be a `.env` file. Follow best practices for your organization for creating deployment credentials.

You will need to set up the following resources to use this module:

* A database. Postgres is recommended, but not required. When the API connects to the database for the first time, it will create the needed database schema.

# Ingesting Data

RESPIRE is data source agnostic. There are many potential sources for gene expression data, so we leave it to individual researchers to gather data from their preferred location. RESPIRE expects the following data structure:

- study_accession (String): The sample's GEO accession number
- gene (String): Gene identifier for the sample
- sample_accession (String): Unique sample ID
- value (String): The value for this combination of 'study_accession', 'gene', and 'sample_accession'

The study_accession, gene, and sample_accession form a compound primary key.
