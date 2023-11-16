bioproject_struct = {
    'root': 'DocumentSummary',
        'vars': [
            { 'name': 'study_id', 'path': None, 'attr': 'uid', 'type': 'int' },
            { 'type': 'str', 'attr': None, 'name': 'title', 'path': 'Project/ProjectDescr/Title' },
            { 'type': 'str', 'attr': None, 'name': 'access', 'path': 'Submission/Description/Access' },
            { 'type': 'str', 'attr': None, 'name': 'description', 'path': 'Project/ProjectDescr/Description' },
            { 'type': 'str', 'attr': None, 'name': 'data_type', 'path': 'Project/ProjectType/ProjectTypeSubmission/ProjectDataTypeSet/DataType' },
            { 'type': 'str', 'attr': 'submitted', 'name': 'submitted', 'path': 'Submission' },
            { 'type': 'str', 'attr': None, 'name': 'organization', 'path': 'Submission/Description/Organization/Name' },
            { 'type': 'str', 'attr': None, 'name': 'organism_name', 'path': 'Project/ProjectType/ProjectTypeSubmission/Target/Organism/OrganismName' },
            { 'type': 'str', 'attr': 'species', 'name': 'organism_id', 'path': 'Project/ProjectType/ProjectTypeSubmission/Target/Organism' },
            { 'type': 'str', 'attr': 'db', 'name': 'external_db', 'path': 'Project/ProjectDescr/ExternalLink/dbXREF' },
            { 'type': 'str', 'attr': None, 'name': 'external_db_id', 'path': 'Project/ProjectDescr/ExternalLink/dbXREF/ID' },
            { 'type': 'str', 'attr': None, 'name': 'accession_number', 'path': 'Project/ProjectDescr/ExternalLink/dbXREF/ID' },
            # { 'type': 'str', 'attr': 'id', 'name': 'link_id', 'path': 'ProjectLinks/Link/Hierarchical/MemberID' }
        ]
}