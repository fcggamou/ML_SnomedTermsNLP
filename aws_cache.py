import os
from utils import download_file_from_S3, unzip_file
import config
import file_utils
import text_utils
import sys
import shutil
import train_data


def recreate_search_index():

    print('Refreshing terms...')
    terms = train_data.sql_to_df("SELECT Code, Description, Domain FROM Term WHERE Active=1")
    terms.index = terms['Code']
    terms.drop('Code', axis=1, inplace=True)
    file_utils.dump_to_file(terms, os.path.join(config.data_path, 'Term.pkl'))

    print('Refreshing synonyms...')
    syn = train_data.sql_to_df("SELECT Code, Text as Description, Domain FROM Synonym JOIN Term on TermCode=Code WHERE Synonym.Active=1")
    syn.index = syn['Code']
    syn.drop('Code', axis=1, inplace=True)
    file_utils.dump_to_file(syn, os.path.join(config.data_path, 'Synonym.pkl'))

    print('Recreating index...')
    terms = file_utils.load_from_file(os.path.join(config.data_path, 'Term.pkl'))
    synonyms = file_utils.load_from_file(os.path.join(config.data_path, 'Synonym.pkl'))

    terms.reset_index(inplace=True)
    synonyms.reset_index(inplace=True)
    terms['Is_Synonym'] = False
    synonyms['Is_Synonym'] = True

    search = terms.copy()
    search = search.merge(synonyms, how='outer')
    search['Search'] = search['Description'].apply(text_utils.remove_tildes).str.lower()
    search['Length'] = search['Description'].str.len()
    search.reset_index(inplace=True)

    search = search.sort_values(by='Length', ascending=True)
    search = search.set_index(search['Code'])
    search.drop('Code', axis=1, inplace=True)
    search['Synonyms'] = search.groupby('Code')['Description'].apply(list)  # noqa

    file_utils.dump_to_file(search, os.path.join(config.data_path, config.search_index_path))


def main(force, recreate_index):
    for model in config.models_to_download:
        zip_file = model + '.zip'
        download_file_from_S3(zip_file, force=force)
        if force and os.path.exists(os.path.join(config.models_path, model)):
            shutil.rmtree(os.path.join(config.models_path, model))
        if not os.path.exists(os.path.join(config.models_path, model)):
            unzip_file(os.path.join(config.models_path, zip_file), os.path.join(config.models_path, model))

    if recreate_index:
        recreate_search_index()
    # else:
    #     download_file_from_S3(config.search_index_path, config.data_path, force)


if __name__ == '__main__':
    args = sys.argv[1:]
    force = '-force' in args
    recreate_index = '-index' in args
    main(force, recreate_index)
