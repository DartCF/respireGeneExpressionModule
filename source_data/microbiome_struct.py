#%%
microbiome_struct = {
    'root': 'DocumentSummary',
        'vars': [
            { 'name': 'study_id', 'path': None, 'attr': 'uid', 'type': 'int' },
            { 'type': 'str', 'attr': None, 'name': 'title', 'path': 'Project/ProjectDescr/Title' },
            { 'type': 'str', 'attr': None, 'name': 'access', 'path': 'Submission/Description/Access' },
            { 'type': 'str', 'attr': None, 'name': 'description', 'path': 'Project/ProjectDescr/Description' },
            { 'type': 'str', 'attr': None, 'name': 'data_type', 'path': 'Project/ProjectType/ProjectTypeSubmission/ProjectDataTypeSet/DataType' },
            { 'type': 'str', 'attr': 'submitted', 'name': 'submitted', 'path': 'Submission' },
            { 'type': 'str', 'attr': None, 'name': 'organization', 'path': 'Submission/Description/Organization/Name' },
            { 'type': 'str', 'attr': 'accession', 'name': 'accession_number', 'path': 'Project/ProjectID/ArchiveID' },
            { 'type': 'str', 'attr': 'method_type', 'name': 'method', 'path': 'Project/ProjectType/ProjectTypeSubmission/Method' },
        ]
}
# %%
