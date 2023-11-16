# %%
from Bio import Entrez
from Bio.Entrez import esearch, efetch
import xml.etree.ElementTree as ET
import pandas as pd
from retry import retry
from .functions import extract_var, get_links, extract_keys, get_ncbi_summary
from .bioproject_struct import bioproject_struct

# from functions import extract_var, get_links, extract_keys, get_ncbi_summary
# from bioproject_struct import bioproject_struct

# %%


class MetadataParser:

    def __init__(self, entrez_email, bioproject_query) -> None:
        Entrez.email = entrez_email
        self.query = bioproject_query
        self.bioproject_xml_struct = bioproject_struct

    def fetch_results(self):
        handle = esearch(db='BioProject',
                         term=self.query,
                         retmax=100000,
                         usehistory='y'
                         )
        # try:
        res = Entrez.read(handle)
        # except:
        #     pass  # exit gracefully
        # finally:
        handle.close()

        # try:
        fetch_handle = efetch(db='bioproject', id=res['IdList'])

        self.results = fetch_handle.read()
        # except:
        #     pass
        # finally:
        fetch_handle.close()

        self.xml = ET.XML(self.results)

        return self

    def parse_search_results(self):
        names = [e['name'] for e in self.bioproject_xml_struct['vars']]
        result_list = self.xml.findall(self.bioproject_xml_struct['root'])

        # pre-allocate space for results -- avoiding nested list comprehension
        rows = [None]*len(result_list)

        # for each result, extract each needed variable and
        for i in range(len(result_list)):
            rows[i] = pd.DataFrame(
                [[extract_var(result_list[i], v) for v in self.bioproject_xml_struct['vars']]], columns=names
            )

        self.study_metadata = pd.concat(rows)
        
        return self

    def link_bioproject_studies(self):
        # sample_metadata = []
        study_samples_meta = []
        failed_studies = []

        for bioproject_id in self.study_metadata.study_id:
            print(f'Attempting link for UID {bioproject_id}')
            try:
                # # link bioporject IDs to GEO data system IDs
                # links = get_links(str(bioproject_id), db_to='gds')

                # # get ID values from results
                # gds_ids = [study_id for study_id in extract_keys(
                #     links, 'Id') if study_id != str(bioproject_id)]
                # # print(gds_ids)

                # # get summary and return as dict
                # # TODO: investigate -- is this always the first element (0)?
                # # I think this is correct, but hard indexing makes me nervous.
                # gds_summary_dict = get_ncbi_summary(gds_ids[0], 'gds')

                # # convert to DataFrame -- need to go in two levels for the needed info
                # gds_summary_df = pd.DataFrame(
                #     gds_summary_dict['eSummaryResult']['DocSum']['Item']
                # )
                # # clean up names
                # gds_summary_df.rename(
                #     columns={
                #         '@Name': 'name',
                #         '@Type': 'type',
                #         '#text': 'text',
                #         'Item': 'item'
                #     },
                #     inplace=True,
                # )

                # # filter for useful information in the name column
                # data_summary = gds_summary_df.loc[
                #     gds_summary_df.name.isin(
                #         ['Accession', 'taxon', 'entryType', 'gdsType', 'n_samples']
                #     )
                # ][['name', 'text']].reset_index()

                # # add bioproject ID for linking
                # data_summary['study_id'] = int(bioproject_id)

                # # pivot data to single record
                # data_summary = data_summary.set_index(
                #     'study_id'
                # ).pivot(
                #     columns='name', values='text'
                # ).reset_index()

                # # clean up names
                # data_summary.rename(
                #     columns={
                #         'Accession': 'accession_number',
                #         'entryType': 'entry_type',
                #         'gdsType': 'gds_type',
                #         'taxon': 'species'
                #     },
                #     inplace=True
                # )
                # # add gds ID for reference later
                # data_summary['gds_id'] = gds_ids[0]

                # # extract samples
                # sample_list = list(gds_summary_df.loc[
                #     # filter for samples, then extract the object stored in that row
                #     gds_summary_df.name == 'Samples'
                # ][['item']].iloc[0:].item)[0]

                # samples = pd.concat([pd.DataFrame(i['Item']) for i in sample_list])

                # # need to have an index that goes 1, 1, 2, 2, 3, 3, etc.
                # # constructing list for that purpose
                # idxlst = []
                # for i in range(len(sample_list)):
                #     idxlst.append(i)
                #     idxlst.append(i)

                # # create ID col as index
                # samples['id'] = idxlst

                # sample_ids = samples.set_index(
                #     'id'
                # ).pivot(
                #     columns='@Name', values='#text'
                # ).reset_index(
                # )[['Accession', 'Title']]

                # # add study id for linking
                # sample_ids['study_id'] = int(bioproject_id)

                # # clean up names
                # sample_ids.rename(
                #     columns={
                #         'Title': 'sample_title',
                #         'Accession': 'sample_accession'
                #     },
                #     inplace=True
                # )

                study_samples_meta.append(
                    source_links(bioproject_id)
                )

            except:
                failed_studies.append(bioproject_id)
                print(f'Data load failed for ID {bioproject_id}')

        self.summary_metadata = pd.concat(study_samples_meta).astype('str')

        return self
        
    def export_study_metadata(self):
        merged_data = pd.merge(self.study_metadata,
                               self.summary_metadata[[
                                   'study_id', 'gds_type', 'n_samples']],
                               on='study_id'
                               )
        return merged_data.to_dict(orient='records')

    def export_gds_ids(self):
        return self.gds_ids
# %%


@retry(tries=3, delay=2, backoff=2)
def source_links(bioproject_id):
    # link bioporject IDs to GEO data system IDs
    links = get_links(str(bioproject_id), db_to='gds')

    # get ID values from results
    gds_ids = [study_id for study_id in extract_keys(
        links, 'Id') if study_id != str(bioproject_id)]
    # print(gds_ids)

    # get summary and return as dict
    # TODO: investigate -- is this always the first element (0)?
    # I think this is correct, but hard indexing makes me nervous.
    gds_summary_dict = get_ncbi_summary(gds_ids[0], 'gds')

    # convert to DataFrame -- need to go in two levels for the needed info
    gds_summary_df = pd.DataFrame(
        gds_summary_dict['eSummaryResult']['DocSum']['Item']
    )
    # clean up names
    gds_summary_df.rename(
        columns={
            '@Name': 'name',
            '@Type': 'type',
            '#text': 'text',
            'Item': 'item'
        },
        inplace=True,
    )

    # filter for useful information in the name column
    data_summary = gds_summary_df.loc[
        gds_summary_df.name.isin(
            ['Accession', 'taxon', 'entryType', 'gdsType', 'n_samples']
        )
    ][['name', 'text']].reset_index()

    # add bioproject ID for linking
    data_summary['study_id'] = int(bioproject_id)

    # pivot data to single record
    data_summary = data_summary.set_index(
        'study_id'
    ).pivot(
        columns='name', values='text'
    ).reset_index()

    # clean up names
    data_summary.rename(
        columns={
            'Accession': 'accession_number',
            'entryType': 'entry_type',
            'gdsType': 'gds_type',
            'taxon': 'species'
        },
        inplace=True
    )
    # add gds ID for reference later
    data_summary['gds_id'] = gds_ids[0]

    return data_summary
# %%
