from enums import Model
import locale
model = Model.SIMILARITY

# Similarity

Sim_Phrases_name = 'NER_Phrases_tfr_v4'
Sim_Terms_name = 'NER_All_v1'
Sim_Model = 'SIM_Reduced_v1'
Sim_Embeddings = 'emb.pkl'
Sim_Qualifier_Embeddings = 'emb_q.pkl'
Sim_TermCodes = 'termcodes.pkl'
Sim_QualifierCodes = 'qualifiercodes.pkl'
sim_threshold = 0.8
SIM_Test_TermCodes = 'test_termcodes.pkl'
SIM_Test_Embeddings = 'test_emb.pkl'

# NER
NER_Qualifiers_name = 'NER_Qualifiers_tfr_v4'
NER_Values_name = 'NER_Values_t2v_v3'
NER_Phrases_name = 'NER_Phrases_tfr_v4'
NER_Terms_name = 'NER_Terms_tfr_v3'

models_to_download = [Sim_Phrases_name, Sim_Terms_name, Sim_Model]

# Spellchecking
spellchecker_name = 'spellchecker.pkl'
spellchecker_zip_path = 'spellchecker.zip'
spellchecker_dest = 'spellchecker'
spellchecker_max_distance = 0
spèllchecker_min_length = 4

# Misc

models_path = 'models'
S3_bucket = 'braincraft'
search_index_path = 'search_index.pkl'
data_path = 'data'
max_ehrtext_length = 0

# Database
enable_log = True
sql_log_conn = 

sql_training_conn = 
sql_test_conn = 

decimal_char = locale.localeconv()['decimal_point']

CSS = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">'
