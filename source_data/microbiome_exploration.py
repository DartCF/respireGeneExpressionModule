# %%
from Bio import Entrez
from Bio.Entrez import esearch, efetch
import xml.etree.ElementTree as ET
import pandas as pd
from retry import retry
from functions import extract_var, get_links, extract_keys, get_ncbi_summary
# from bioproject_struct import bioproject_struct
import xmltodict
from microbiome_struct import microbiome_struct
#%%
bioproject_ids = ['935808',
'922818',
'918386',
'907661',
'916730',
'890142',
'888325',
'882622',
'880638',
'875913',
'868415',
'861712',
'859087',
'858534',
'858501',
'856555',
'856165',
'843353',
'842324',
'839435',
'837989',
'823005',
'810321',
'808003',
'806679',
'804973',
'801882',
'800766',
'800055',
'799401',
'796908',
'795487',
'790037',
'789321',
'788785',
'786764',
'784956',
'782662',
'782645',
'903920',
'899808',
'866654',
'841251',
'822004',
'816035',
'782204',
'780512',
'773421',
'773392',
'769290',
'765567',
'761508',
'754787',
'753920',
'753762',
'751792',
'749564',
'747222',
'747221',
'746689',
'746114',
'744167',
'743634',
'742691',
'742244',
'742164',
'740243',
'736292',
'722991',
'721302',
'720126',
'717158',
'715451',
'714758',
'714488',
'713502',
'706726',
'702771',
'694574',
'687361',
'687143',
'685554',
'683885',
'683617',
'679593',
'678252',
'675235',
'675110',
'673153',
'672792',
'668745',
'666192',
'664034',
'662963',
'658040',
'656590',
'650559',
'647170',
'646239',
'645089',
'644285',
'644204',
'637544',
'635571',
'630042',
'626477',
'626157',
'624822',
'614587',
'611611',
'609242',
'606061',
'605315',
'602744',
'599290',
'595346',
'592147',
'590873',
'589852',
'580164',
'578082',
'572916',
'559069',
'554822',
'552813',
'550234',
'548720',
'548310',
'547921',
'544655',
'541144',
'539959',
'535518',
'533819',
'531152',
'530252',
'527997',
'522449',
'520921',
'518155',
'516870',
'516066',
'515689',
'515279',
'515255',
'512576',
'509177',
'508342',
'504987',
'503799',
'501806',
'495242',
'492954',
'492500',
'491749',
'485626',
'478900',
'478762',
'477678',
'474717',
'472758',
'464268',
'450850',
'450137',
'439311',
'437613',
'434133',
'422117',
'419524',
'408304',
'401190',
'400142',
'399868',
'397867',
'396749',
'392856',
'391776',
'388464',
'386984',
'385888',
'381268',
'380493',
'377739',
'371442',
'361129',
'360332',
'357063',
'356232',
'339931',
'339813',
'327258',
'326122',
'325608',
'324792',
'324582',
'321607',
'319185',
'305886',
'305761',
'305470',
'303190',
'303160',
'302453',
'299510',
'299077',
'294397',
'294396',
'290599',
'288589',
'284462',
'269493',
'267584',
'256169',
'254115',
'253931',
'253761',
'252825',
'257112',
'246158',
'246028',
'241408',
'231159',
'223375',
'210948',
'172839',
'170783']
#%%
Entrez.email = 'matthew.rogers@dartmouth.edu'
#935808
#717158
#%%
metadata = []
for bioproject_uid in bioproject_ids:
    try:
        # bioproject_uid = '882622'
        fetch_handle = efetch(db='bioproject', id=[bioproject_uid])

        results = fetch_handle.read()
        fetch_handle.close()
        xml = ET.XML(results)

        names = [e['name'] for e in microbiome_struct['vars']]
        result_list = xml.findall(microbiome_struct['root'])

        # pre-allocate space for results -- avoiding nested list comprehension
        rows = [None]*len(result_list)

        # for each result, extract each needed variable and
        for i in range(len(result_list)):
            rows[i] = pd.DataFrame(
                [[extract_var(result_list[i], v) for v in microbiome_struct['vars']]], columns=names
            )

        study_metadata = pd.concat(rows)


        # project_dict = xmltodict.parse(results)

        links = get_links(db_from='bioproject', db_to='sra', study_id=bioproject_uid)
        print(links)

        sra_ids = [e['Id'] for e in links['eLinkResult']['LinkSet']['LinkSetDb'][0]['Link']]



        # source for all accessions
        # us accessions to get bioproject IDs
        # bioproject IDs to get SRA IDs
        # count of SRA IDs for nsamples


        sra_fetch_handle = efetch(db='sra', id=sra_ids)

        sra_results = sra_fetch_handle.read()

        sra_xml = ET.XML(sra_results)


        sra_res_dict = xmltodict.parse(sra_results)
        sra_fetch_handle.close()

        # experiment = sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'][0]['EXPERIMENT']
        # submission = sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'][0]['SUBMISSION']
        # study = sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'][0]['STUDY']
        #
        # sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'][0]['SAMPLE']['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE']

        sample_info = []

        for i in range(len(sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'])):
            record_dict = {}
            current_record = sra_res_dict['EXPERIMENT_PACKAGE_SET']['EXPERIMENT_PACKAGE'][i]
            for j in range(len(current_record['SAMPLE']['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE'])):
                current_attribute = current_record['SAMPLE']['SAMPLE_ATTRIBUTES']['SAMPLE_ATTRIBUTE'][j]
                record_dict[current_attribute['TAG']] = current_attribute['VALUE']
            sample_info.append(record_dict)

        # 
        # data_df = pd.DataFrame.from_dict(sample_info)
        study_metadata['n_samples'] = len(sample_info)

        if 'host' in sample_info[0].keys():
            study_metadata['host'] = sample_info[0]['host']
        else:
            study_metadata['host'] = None

        if 'BioSampleModel' in sample_info[0].keys():
            study_metadata['bio_sample_model'] = sample_info[0]['BioSampleModel']
        else:    
            study_metadata['bio_sample_model'] = None
        metadata.append(study_metadata)
    except:
        print(f"Failed to fetch {bioproject_uid}")
# %%
all_metadata = pd.concat(metadata)
# %%
# generate counts of each host
host_counts = all_metadata.groupby('host').count()['n_samples']
# %%
all_metadata.to_csv('all_microbiome_metadata.csv')
# %%
import pandas as pd
# %%
all_metadata = pd.read_csv('all_microbiome_metadata.csv')
# %%
constr = ""

# %%
from sqlalchemy import create_engine
# %%
engine = create_engine(constr)
#%%
# remove Unnamed: 0 column
all_metadata = all_metadata.drop(columns=['Unnamed: 0'])
# %%
with engine.connect() as conn:
    all_metadata.to_sql('studies', conn, if_exists='replace', index=False)
# %%
bioproject_uid = bioproject_ids[0]
fetch_handle = efetch(db='bioproject', id=[bioproject_uid])

results = fetch_handle.read()
fetch_handle.close()
xml = ET.XML(results)
# %%
xmltodict.parse(results)
# %%
