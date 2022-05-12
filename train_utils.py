import spacy
from spacy.training import offsets_to_biluo_tags, biluo_tags_to_spans
import re
import text_utils
import string
from spacy.tokens import DocBin
import random


class TrainSetGenerator():
    def __init__(self, test_size, columns, shuffle=True, remove_punc=False, train_path='train.spacy', test_path='test.spacy', merge_overlapped_terms=False, one_example_per_label=True):
        self.test_size = test_size
        self.shuffle = shuffle
        self.remove_punc = remove_punc
        self.train_path = train_path
        self.test_path = test_path
        self.merge_overlapped_terms = merge_overlapped_terms
        self.columns = columns
        self.one_example_per_label = one_example_per_label

    # --- NER ---

    def pre_process(self, data):
        fix_backward_tildes(data, self.columns)
        data[self.columns] = data[self.columns].applymap(str.lower)
        if self.remove_punc:
            remove_punc(data, self.columns)

        for column in self.columns:
            data[column] = data[column].apply(text_utils.separate_punct)
            data[column] = data[column].apply(lambda x: x.strip(string.punctuation + ' '))
            data[column] = data[column].apply(text_utils.fix_double_spaces)

        return data

    def get_train_set(self, df, entity_column, text_column, label_column):
        """ Returns the NER training set """

        df = self.pre_process(df)

        df['Span'] = df.apply(find_whole_term, args=((entity_column, text_column)), axis=1)
        df.dropna(inplace=True)
        df['Entity'] = df.apply(lambda x: (int(x['Span'][0]), int(x['Span'][1]), x[label_column]), axis=1)

        train = []
        for x, y in df.groupby(by=text_column):
            entities = []
            for term in y['Entity']:
                if term[2] != '':
                    overlaps = [e for e in entities if overlap(term, e)]
                    if len(overlaps) > 0:
                        overlaps.append(term)
                        term = self.merge_overlaps(overlaps)

                        entities = [x for x in entities if x not in overlaps]

                    entities.append(term)
            train.append((x, {'entities': entities}))

        train = trim_entity_spans(train)
        return train

    def generate_train_files(self, train_data):
        """ Gets the NER training set and saves it into train and test files, optionally including examples from synonyms and terms """
        train, test = split_data(train_data, self.test_size, self.shuffle, self.one_example_per_label)
        train = train_set_to_docs(train)
        test = train_set_to_docs(test)
        train_bin = DocBin(docs=train)
        test_bin = DocBin(docs=test)
        train_bin.to_disk(self.train_path)
        test_bin.to_disk(self.test_path)

    def merge_overlaps(self, overlaps):
        """ Deals with overlapping entities, either merges them into one or returns the biggest. """
        if self.merge_overlapped_terms:
            min_start = min([x[0] for x in overlaps])
            max_end = max([x[1] for x in overlaps])
            label = '.'.join(sorted(set([x[2] for x in overlaps])))
            return min_start, max_end, label
        else:
            return max(overlaps, key=lambda x: x[1] - x[0])


def split_data(data, test_size, shuffle, one_example_per_label=False):
    """ Splits a list into train and test, optionally shuffling it """
    if shuffle:
        random.shuffle(data)
    if one_example_per_label:
        n_test = int(len(data) * test_size)
        codes = []
        train = []
        for text in data:
            text_codes = [x[2] for x in text[1]['entities']]
            if any([x not in codes for x in text_codes]):
                train.append(text)
                data.remove(text)
                codes.extend(text_codes)

        train.extend(data[:-n_test])
        test = data[-n_test:]
    else:
        train = data[:-int(len(data) * test_size)]
        test = data[-int(len(data) * test_size):]
    if shuffle:
        random.shuffle(train)
        random.shuffle(test)

    return train, test


def train_set_to_docs(train_set):
    """ Converts a NER training set into a list of spacy.doc objects """
    nlp = spacy.load('es_core_news_md')
    docs = []
    for text, annot in train_set:
        doc = nlp(text)
        tags = offsets_to_biluo_tags(doc, annot['entities'])
        entities = biluo_tags_to_spans(doc, tags)
        doc.ents = entities
        docs.append(doc)

    return docs


def overlap(e1, e2):
    """ Returns true if the intervals e1 and e2 overlap """
    start1, end1 = e1[0], e1[1]
    start2, end2 = e2[0], e2[1]
    return start1 >= start2 and end1 <= end2 or\
        start1 >= start2 and start1 <= end2 or\
        start2 >= start1 and end2 <= end1 or\
        start2 >= start1 and start2 <= end1


def trim_entity_spans(data: list) -> list:
    """Removes leading and trailing white spaces from entity spans.

    Args:
        data (list): The data to be cleaned in spaCy format.

    Returns:
        list: The cleaned data.
    """
    invalid_span_tokens = re.compile(r'[\s\.\,\'\"]')
    word_end = re.compile(r'\s')
    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(
                    text[valid_end - 1]):
                valid_end -= 1

            while valid_start > 0 and not word_end.match(text[valid_start - 1]):
                valid_start -= 1

            while valid_end < len(text) and not word_end.match(text[valid_end]):
                valid_end += 1
            if not any([overlap((valid_start, valid_end), e) for e in valid_entities]):
                valid_entities.append([valid_start, valid_end, label])

            ent = text[valid_start:valid_end]
            if ent == '-':
                print(ent)
        cleaned_data.append([text, {'entities': valid_entities}])

    return cleaned_data


def remove_punc(train_data, columns):
    """ Replaces punctuation in a train set dataframe """
    for column in columns:
        train_data[column] = train_data[column].apply(text_utils.remove_punc)


def fix_backward_tildes(train_data, columns):
    """ Fixes tildes that are backwards e.g. changes 'è' to 'é'  """
    for column in columns:
        train_data[column] = train_data[column].apply(text_utils.fix_tildes)


def find_whole_term(x, term_column, text_column):
    """ Returns the start and end index of the term in the text """
    result = list(re.finditer(r'\b' + re.escape(x[term_column]) + r'\b', x[text_column]))
    if len(result) > 0:
        return result[0].span()
    return None


def add_missing_labels(nlp, tg, output_path='ner'):
    nlp = spacy.load('model-best')
    train = tg.get_train_data()
    codes = []
    for t in train:
        for e in t[1]['entities']:
            if e[2] not in codes:
                codes.append(e[2])

    codes_not_added = [x for x in codes if x not in nlp.get_pipe('ner').labels]
    print(codes_not_added)
    for code in codes_not_added:
        nlp.get_pipe('ner').add_label(code)
    if output_path is not None:
        nlp.to_disk(output_path)
