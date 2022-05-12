from snomed import Snomed


def test_search_term_partial_match():

    terms = Snomed.instance().search_by_description('hipertensión', False)
    assert all(['hipertensión' in x.description for x in terms])


def test_search_by_description():

    terms = Snomed.instance().search_by_description('hipertensión arte')
    assert all([('hipertensión' in x.description and 'arte' in x.description) for x in terms])
    assert terms[0].description == 'hipertensión arterial'
    assert terms[0].code == '38341003'


def test_search_by_description_2():

    terms = Snomed.instance().search_by_description('lesion')
    assert all([('lesión' in x.description or 'lesion' in x.description) for x in terms])
    assert terms[0].description == 'lesión'
    assert terms[0].code == '52988006'


def test_search_by_description_3():

    terms = Snomed.instance().search_by_description('atendido ginecologo')
    assert all([('atendido' in x.description and 'ginecólogo' in x.description) for x in terms])
    assert terms[0].description == 'atendido por un ginecólogo'
    assert terms[0].code == '305690005'


def test_search_by_description_4():

    terms = Snomed.instance().search_by_description('eSchERIchiA cOLi')
    assert all([('Escherichia' in x.description and 'coli' in x.description) for x in terms])
    assert terms[0].description == 'Escherichia coli'
    assert terms[0].code == '112283007'


def test_search_by_code():

    term = Snomed.instance().search_by_code('38341003')
    assert term.code == '38341003'


def test_search_by_description_ignore_tildes():

    terms = Snomed.instance().search_by_description('hipertension arte')
    assert all(['hipertensión' in x.description for x in terms])
    assert terms[0].description == 'hipertensión arterial'
    assert terms[0].code == '38341003'


def test_search_by_description_exact_match():

    terms = Snomed.instance().search_by_description('hipertension arterial', True)
    assert len(terms) == 1
    assert terms[0].description == 'hipertensión arterial'
    assert terms[0].code == '38341003'
