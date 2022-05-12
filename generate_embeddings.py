from model.model_factory import get_model
import config
import enums
from model.sim_model import SIMModel
import train_data
import file_utils
import os

config.model = enums.Model.SIMILARITY

model: SIMModel = get_model()

qualifiers = train_data.sql_to_df('SELECT QualifierCode FROM Qualifier')
ehrQualifiers = file_utils.load_from_file('data/Training/EHRQualifiers.pkl')
terms = file_utils.load_from_file(os.path.join('data', 'Term.pkl'))
synonyms = file_utils.load_from_file(os.path.join('data', 'Synonym.pkl'))

terms['TermCode'] = terms.index
terms.reset_index(drop=True, inplace=True)

terms = terms[terms['TermCode'].isin(qualifiers['QualifierCode'])]

synonyms['TermCode'] = synonyms.index
synonyms.reset_index(drop=True, inplace=True)
synonyms = synonyms[synonyms['TermCode'].isin(terms['TermCode'].values)]

ehrQualifiers.dropna(inplace=True)
ehrQualifiers = ehrQualifiers.groupby("QualifierText").agg(lambda x: x.value_counts().index[0])
ehrQualifiers['Description'] = ehrQualifiers.index
ehrQualifiers.drop('Phrase', axis=1, inplace=True)
ehrQualifiers.drop('Text', axis=1, inplace=True)
ehrQualifiers.columns = ['TermCode', 'Description']
ehrQualifiers.reset_index(drop=True, inplace=True)

terms = terms.append(synonyms)
terms = terms.append(ehrQualifiers)
terms['Description'] = terms['Description'].str.lower()
terms = terms.drop_duplicates()
terms.reset_index(drop=True, inplace=True)

emb = model.sim.encode(terms['Description'], convert_to_tensor=True, normalize_embeddings=True)
file_utils.dump_to_file(emb, 'emb_qualifiers.pkl')
file_utils.dump_to_file(terms['TermCode'], 'qualifiercodes.pkl')
