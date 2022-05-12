from nlp_service import NLPService


nlp = NLPService()


def test_predict():
    text = 'hta. no af cancer de colon'
    prediction = nlp.predict(text)

    assert prediction is not None
    assert len(prediction.phrases) == 2
    assert len(prediction.phrases[0].terms) == 1
    assert prediction.phrases[0].terms[0].code == '38341003'
    assert prediction.phrases[0].terms[0].description == 'trastorno hipertensivo arterial sistémico'
    assert prediction.phrases[0].terms[0].domain == 'trastorno'
    assert len(prediction.phrases[0].terms[0].qualifiers) == 0

    assert len(prediction.phrases[1].terms) == 1
    assert prediction.phrases[1].terms[0].code == '312824007'
    assert prediction.phrases[1].terms[0].description == 'antecedente familiar de cáncer de colon'
    assert prediction.phrases[1].terms[0].domain == 'situación'
    assert len(prediction.phrases[1].terms[0].qualifiers) == 1
    assert prediction.phrases[1].terms[0].qualifiers[0].code == '410516002'
    assert prediction.phrases[1].terms[0].qualifiers[0].description == 'ausencia conocida'
    assert prediction.phrases[1].terms[0].qualifiers[0].domain == 'calificador'


def test_predictv2():
    text = 'tu y td normal'
    prediction = nlp.predict(text)
    assert prediction is not None
    assert len(prediction.phrases) == 1
    assert len(prediction.phrases[0].terms) == 2

    assert prediction.phrases[0].terms[0].code == '432045005'
    assert prediction.phrases[0].terms[0].description == 'tracto urinario propiamente dicho [como un todo]'
    assert prediction.phrases[0].terms[0].domain == 'estructura corporal'
    assert len(prediction.phrases[0].terms[0].qualifiers) == 1
    assert prediction.phrases[0].terms[0].qualifiers[0].code == '17621005'
    assert prediction.phrases[0].terms[0].qualifiers[0].description == 'normal'
    assert prediction.phrases[0].terms[0].qualifiers[0].domain == 'calificador'

    assert prediction.phrases[0].terms[1].code == '731977000'
    assert prediction.phrases[0].terms[1].description == 'tracto digestivo [como un todo]'
    assert prediction.phrases[0].terms[1].domain == 'estructura corporal'
    assert len(prediction.phrases[0].terms[1].qualifiers) == 1
    assert prediction.phrases[0].terms[1].qualifiers[0].code == '17621005'
    assert prediction.phrases[0].terms[1].qualifiers[0].description == 'normal'
    assert prediction.phrases[0].terms[1].qualifiers[0].domain == 'calificador'


def test_predictv2_values():
    text = 'ldl 80'
    prediction = nlp.predict(text)
    assert prediction is not None
    assert len(prediction.phrases) == 1
    assert len(prediction.phrases[0].terms) == 1
    assert prediction.phrases[0].terms[0].code == '102739008'
    assert prediction.phrases[0].terms[0].description == 'colesterol de lipoproteína de baja densidad'
    assert prediction.phrases[0].terms[0].domain == 'sustancia'
    assert len(prediction.phrases[0].terms[0].values) == 1
    assert prediction.phrases[0].terms[0].values[0].value == 80
    assert prediction.phrases[0].terms[0].values[0].text == '80'


def test_predict_qualifier():

    text = 'normal'
    prediction = nlp.predict_qualifier(text)
    assert prediction.code == '17621005'
    assert prediction.description == 'normal'
    assert prediction.domain == 'calificador'
    assert prediction.to_snomed == '17621005 |normal|'
