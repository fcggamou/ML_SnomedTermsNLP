import pandas as pd
import train_utils
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def get_reduced_train_data():
    df = pd.DataFrame([['trastorno', '38341003', 'hipertension arterial', 'tiene hipertension arterial sabelo', ],
                       ['trastorno', '12345678', 'cefaleas', 'tambien cefaleas ocasionalmente']], columns=['Domain', 'TermCode', 'TermText', 'Text'])
    return df


def test_get_train_set():

    df = get_reduced_train_data()
    tg = train_utils.TrainSetGenerator(0.1, ['TermText', 'Text'])
    train = tg.get_train_set(df, 'TermText', 'Text', 'TermCode')
    assert(train[0] == ['tambien cefaleas ocasionalmente', {'entities': [[8, 16, '12345678']]}])
    assert(train[1] == ['tiene hipertension arterial sabelo', {'entities': [[6, 27, '38341003']]}])


def test_split_data():
    a = [1, 2, 3, 4, 5, 6, 7, 8]
    train, test = train_utils.split_data(a, 0.25, False)
    assert(train == [1, 2, 3, 4, 5, 6])
    assert(test == [7, 8])


def test_find_whole_term():
    text = 'estudio. tu y td normal'
    df = pd.DataFrame([['tu', text], ['td', text]], columns=['TermText', 'Text'])
    df['Span'] = df.apply(train_utils.find_whole_term, axis=1, args=(('TermText', 'Text')))

    assert text[df.iloc[0]['Span'][0]:df.iloc[0]['Span'][1]] == 'tu'
    assert text[df.iloc[1]['Span'][0]:df.iloc[1]['Span'][1]] == 'td'


def test_merge_overlaps():
    tg = train_utils.TrainSetGenerator(0.1, ['TermText', 'Text'], merge_overlapped_terms=True)
    term1 = [0, 10, 'a']
    term2 = [0, 10, 'b']
    term3 = [0, 10, 'b']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == (0, 10, 'a.b')

    term1 = [2, 10, 'a']
    term2 = [5, 15, 'b']
    term3 = [7, 9, 'c']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == (2, 15, 'a.b.c')

    term1 = [1, 10, 'a']
    term2 = [10, 20, 'b']
    term3 = [20, 30, 'c']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == (1, 30, 'a.b.c')


def test_merge_overlaps_bigger_term():
    tg = train_utils.TrainSetGenerator(0.1, ['TermText', 'Text'], merge_overlapped_terms=False)
    term1 = [0, 10, 'a']
    term2 = [0, 11, 'b']
    term3 = [0, 12, 'b']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == [0, 12, 'b']

    term1 = [2, 10, 'a']
    term2 = [5, 15, 'b']
    term3 = [7, 9, 'c']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == [5, 15, 'b']

    term1 = [1, 10, 'a']
    term2 = [10, 22, 'b']
    term3 = [20, 35, 'c']

    merged_term = tg.merge_overlaps([term1, term2, term3])

    assert merged_term == [20, 35, 'c']
