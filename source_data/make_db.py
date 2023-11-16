if __name__ == "__main__":
    #%%
    import pandas as pd
    import os
    import sqlite3
    from sqlite3 import Error
    import json
    import re
    from functions import run_fast_scandir, connect_to_db

    #%%

    def process_file(fp):
        cpdia = pd.read_csv(fp, sep = "\t")

        value_cols = [c for c in cpdia.columns if c not in ['Gene', 'index']]
        
        cpdia_long = cpdia.melt(id_vars=['Gene'], value_vars=value_cols)
        experiment = re.search(r"(?<=/)\w+(?=/)", fp).group()
        
        cpdia_long['experiment'] = experiment

        return cpdia_long
                
    #%%
    subfolders, files = run_fast_scandir("refine_bio_download", [".tsv"])
    #%%
    metadata_files = [f for f in files if "metadata" in f.lower()]
    
    compendia = [f for f in files if "metadata" not in f.lower()]

    samples = pd.concat([pd.read_csv(f, sep="\t") for f in metadata_files])
    processed_compendia = pd.concat([process_file(f) for f in compendia])

    gene_counts = processed_compendia.groupby(['Gene', 'experiment'])['Gene'].count().reset_index(name = 'count')
    #%%
    with open("refine_bio_download/aggregated_metadata.json") as fp:
       agg_meta = json.load(fp)
    
    metadata = pd.DataFrame().from_dict(agg_meta['experiments'], orient='index')

    metadata['n_samp'] = [len(e) for e in metadata.sample_accession_codes]
    #%%
    metadata['source_first_published'] = metadata['source_first_published'].astype('str')
    metadata['source_last_modified'] = metadata['source_last_modified'].astype('str')
    
    for col in metadata.columns:
        if isinstance(metadata[col][0], list):
            metadata[col] = [','.join(map(str, l)) for l in metadata[col]]
            
    metadata.drop('has_publication', axis = 1, inplace=True)
    metadata.drop('publication_doi', axis = 1, inplace=True)
    metadata.drop('submitter_institution', axis = 1, inplace=True)
    #%%
    con = connect_to_db("coders_sqlite.db")
    #%%
    metadata.to_sql("metadata", con, index=False, if_exists="replace")
    
    #%%
    samples.to_sql("sample_metadata", con, index=False, if_exists="replace")

    #%% 
    gene_counts.to_sql("gene_counts", con, index=False, if_exists='replace')
    #%%
    con.close()

# %%
