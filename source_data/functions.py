
from Bio.Entrez import esummary, elink, efetch
import xmltodict
import xml.etree.ElementTree as ET
import os
import sqlite3
from sqlite3 import Error

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import tempfile
import gzip
import time

def extract_var(xml, db_struct: dict) -> str:
    """Extract a value from an XML packet

    Args:
        xml (_type_): An XML object
        db_struct (dict): A dictionary containing a path and optional attribute

    Returns:
        str: The value of the selected path and attribute
    """

    # extract attribute if present
    if db_struct['attr'] is not None:
        # print('if 1')
        # print(db_struct['attr'])
        if db_struct['path'] is not None:
            # print('if 2')
            return xml.find(db_struct['path']).get(db_struct['attr']) if xml.find(db_struct['path']) is not None else None
        
        return xml.get(db_struct['attr']) if xml.get(db_struct['attr']) is not None else None

        
    
    # otherwise extract text
    return xml.find(db_struct['path']).text if xml.find(db_struct['path']) is not None else None

def extract_keys(dictionary, key) :
    """Extract all instances of a key from a nested dictionary

    Args:
        dictionary (dict): A dictionary, typically nested
        key (str): A dictionary key to search for

    Yields:
        Generator[dict, str, str]: _description_
    """
    if hasattr(dictionary, 'items'):
        for k, v in dictionary.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in extract_keys(v, key):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in extract_keys(d, key):
                        yield result


def get_links(study_id: str, db_from: str = 'bioproject', db_to: str = 'biosample', out: str = 'dict') -> dict:
    """Link an NCBI ID from one NCBI database to another

    Args:
        study_id (str): The study ID for which to retrieve links
        db_from (str, optional): The database containing the study_id. Defaults to 'bioproject'.
        db_to (str, optional): The linked database of interest. Defaults to 'biosample'.
        out (str, optional): Format for output. If 'dict', a dictionary is returned, otherwise an XML object. Defaults to 'dict'.

    Returns:
        dict: A dictionary containing the response
    """

    hndl = elink(db=db_to, dbfrom=db_from, id=study_id)
    res = hndl.read()
    hndl.close()

    if out == 'dict':
        return xmltodict.parse(res)

    return ET.XML(res)


def fetch_ncbi(study_id, db='bioproject', out='dict'):
    handl = efetch(db=db, id=study_id)
    res = handl.read()
    handl.close()

    if out == 'dict':
        return xmltodict.parse(res)

    return ET.XML(res)


def get_ncbi_summary(study_id: str, db: str = 'bioproject', out: str = 'dict'):
    """Retrieve a summary of a study

    Args:
        study_id (str): A valid study ID number
        db (str, optional): Database to search for a summary. Defaults to 'bioproject'.
        out (str, optional): Format for output. If 'dict', a dictionary is returned, otherwise an XML object.. Defaults to 'dict'.

    Returns:
        dict or xml: The response from esummary()
    """

    handl = esummary(db=db, id=study_id)
    res = handl.read()
    handl.close()

    if out == 'dict':
        return xmltodict.parse(res)

    return ET.XML(res)


def run_fast_scandir(dir, ext):    # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)


    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def connect_to_db(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def get_sample_metadata(geo_ids):

    td = tempfile.gettempdir()

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    dta = []

    for geo in geo_ids:
        if geo is None:
            continue
        # substitute the last three digits of the GSE ID for three 'n's
        stub = re.sub(r"\d{3}$", "nnn", geo.upper())

        try:
            gdsurl = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{stub}/{geo.upper()}/matrix/"

            req = requests.get(gdsurl, headers)
            soup = BeautifulSoup(req.content, 'html.parser')

            links = soup.find_all('a')

            vals = [e.attrs['href']
                    for e in links if re.match(r"^G", e.attrs['href'])]

            # print(f"Found {len(vals)} files")
        except:
            return 500
        
        if len(vals) == 0:
            print(f"No files for {geo}, moving on")
            continue

        for i, file in enumerate(vals):
            try:
                # create a temporary filepath
                fp = os.path.join(td, file)

                # write file to temp location
                with open(fp, 'wb') as location:
                    resp = requests.get(gdsurl + file)
                    location.write(resp.content)

                # read content into list of strings
                with gzip.open(fp, "rt") as gzf:
                    file_content = gzf.readlines()

                # find rows that begin with "!Sample" (this is the relevant metadata)
                ptn = re.compile(r"^!Sample")
                sample_idcs = [i for i, v in enumerate(file_content) if ptn.match(v)]

                # get start row and total number of rows that begin with "!Sample"
                sample_start = min(sample_idcs) - 1
                samp_nrows = (max(sample_idcs) - 1) - sample_start

                # read the values in with tab separation, beginning with sample_start and only reading sample_nrows of data
                # then, transpose the data (columns to rows and rows to columns) and reset the index
                meta = pd.read_csv(fp,
                                sep = "\t",
                                skiprows = sample_start,
                                nrows = samp_nrows
                                ).transpose().reset_index()

                # the desired column names are in the first row, rename the columns
                # clean up the repeated "!sample_" text and convert to lower case
                meta.columns = [re.sub(r"!sample_", "", t.lower()) for t in meta.iloc[0]]

                # drop the first row
                meta.drop(0, inplace=True)

                meta['accession_number'] = geo
                meta.rename(columns={"geo_accession":"sample_accession"}, inplace=True)

                dta.append(
                    meta.melt(id_vars=['accession_number', 'sample_accession']).to_dict(orient='records')
                    )
                
                time.sleep(.1)
            except:
                print("arg")
            finally:
                if os.path.isfile(fp):
                    os.remove(fp)

    return dta