import pandas as pd
import text_utils
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def text_fix_tildes():
    fixed = text_utils.fix_tildes('hìpèrtensiòn arterial')
    assert fixed == 'hipertensión arterial'
    fixed = text_utils.fix_tildes('hípírtensión arterial')
    assert fixed == 'hipertensión arterial'


def test_fix_double_spaces():

    df = pd.DataFrame([['hipertension ', 'hipertension   arterial'], ['mucho dolor   en la  pierna',
                                                                      'mucho dolor en la pierna']], columns=['TermText', 'Text'])
    df['Text'] = df['Text'].apply(text_utils.fix_double_spaces)
    df['TermText'] = df['TermText'].apply(text_utils.fix_double_spaces)

    assert len(df) == 2
    assert df.iloc[0]['Text'] == 'hipertension arterial'
    assert df.iloc[0]['TermText'] == 'hipertension '

    assert df.iloc[1]['Text'] == 'mucho dolor en la pierna'
    assert df.iloc[1]['TermText'] == 'mucho dolor en la pierna'


def test_separate_punct():
    text = 'hta.dislipemia?'
    assert text_utils.separate_punct(text) == 'hta . dislipemia ? '

    text = ';hta.dislipemia?!?!?'
    assert text_utils.separate_punct(text) == ' ; hta . dislipemia ?!?!? '

    text = '2.5'
    assert text_utils.separate_punct(text) == '2.5'

    text = '32,87'
    assert text_utils.separate_punct(text) == '32,87'

    text = '123.'
    assert text_utils.separate_punct(text) == '123'

    text = '123.456'
    assert text_utils.separate_punct(text) == '123.456'

    text = '123.456.'
    assert text_utils.separate_punct(text) == '123.456'

    text = '123,456.'
    assert text_utils.separate_punct(text) == '123,456'


def test_revert_separate_punct():

    text = 'hta . dislipemia ? '
    assert 'hta. dislipemia?' == text_utils.revert_separate_punct(text)

    text = 'hta . dislipemia ?!?!? '
    assert 'hta. dislipemia?!?!?' == text_utils.revert_separate_punct(text)

    text = '2.5'
    assert text_utils.revert_separate_punct(text) == '2.5'

    text = '32,87'
    assert text_utils.revert_separate_punct(text) == '32,87'


def test_replace_whole_word():

    assert text_utils.replace_whole_word('dolor controlado', 'controlado', '', True).strip() == 'dolor'
    assert text_utils.replace_whole_word('ap hta', 'ap', '', True).strip() == 'hta'
    assert text_utils.replace_whole_word('buen control de pa', 'control', '', True).strip() == 'buen control de pa'


def test_get_n_grams():
    text = "enviada por cifras de pa elevadas"
    n_grams = text_utils.get_n_grams(text, 2, 2)
    assert len(n_grams) == 5
    assert "enviada por" in n_grams
    assert "por cifras" in n_grams
    assert "cifras de" in n_grams
    assert "de pa" in n_grams
    assert "pa elevadas" in n_grams


def test_get_n_grams_2():
    text = "enviada por cifras de pa elevadas"
    n_grams = text_utils.get_n_grams(text, 2, 3)
    assert len(n_grams) == 9
    assert "enviada por" in n_grams
    assert "por cifras" in n_grams
    assert "cifras de" in n_grams
    assert "de pa" in n_grams
    assert "pa elevadas" in n_grams

    assert "enviada por cifras" in n_grams
    assert "por cifras de" in n_grams
    assert "cifras de pa" in n_grams
    assert "de pa elevadas" in n_grams
