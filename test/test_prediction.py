import prediction
import snomed
import json


def test_json_to_ehrtext():

    json_str = "{\"EHRPhrase\":[{\"EHRTextID\":0,\"expression\":\"polipos vesiculares\",\"Status\":null,\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"snomedCTExpression\":\"197433003 |pólipo de vesícula biliar| : (47429007 |asociado con| = 63727002 |vesicular|)\",\"EHRText\":null,\"User\":null,\"terms\":[{\"EHRTextID\":0,\"Phrase\":null,\"Text\":\"polipos\",\"TermCode\":\"197433003\",\"Status\":null,\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"EHRPhrase\":null,\"qualifiers\":[{\"EHRTextID\":0,\"Phrase\":null,\"Text\":null,\"TermCode\":null,\"QualifierCode\":\"63727002\",\"text\":\"vesiculares\",\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"EHRTerm\":null,\"snomedCTTerm\":{\"Code\":\"63727002\",\"Description\":\"vesicular\",\"Standard\":null,\"Domain\":\"calificador\",\"ParentCode\":null,\"Active\":null,\"Version\":null,\"EHRQualifier\":[],\"EHRTerm\":[],\"Qualifier\":null,\"Synonym\":[],\"Term1\":[],\"Term2\":null},\"User\":null,\"SnomedQualifier\":\"vesicular\"}],\"snomedCTTerm\":{\"Code\":\"197433003\",\"Description\":\"pólipo de vesícula biliar\",\"Standard\":null,\"Domain\":\"trastorno\",\"ParentCode\":null,\"Active\":null,\"Version\":null,\"EHRQualifier\":[],\"EHRTerm\":[],\"Qualifier\":null,\"Synonym\":[],\"Term1\":[],\"Term2\":null},\"User\":null,\"values\":[],\"Description\":\"pólipo de vesícula biliar\",\"Domain\":\"trastorno\"}]}],\"User\":null,\"ID\":150335,\"Text\":\"polipos vesiculares.\",\"Type\":\"MotivoDeConsulta\",\"Speciality\":\"Medicina Interna\",\"Status\":\"Revisado\",\"UserName\":\"admin\",\"Uptime\":\"2021-04-06T10:15:44.1315811-03:00\"}"
    json_dic = json.loads(json_str)
    ehrtext = prediction.json_to_ehrtext(json_dic)
    assert ehrtext is not None
    assert ehrtext.status == 'Revisado'
    assert ehrtext.text == 'polipos vesiculares.'
    assert ehrtext.uptime == '2021-04-06T10:15:44.1315811-03:00'
    assert ehrtext.username == 'admin'
    assert len(ehrtext.phrases) == 1

    assert len(ehrtext.phrases[0].terms) == 1
    assert ehrtext.phrases[0].text == 'polipos vesiculares'
    assert ehrtext.phrases[0].terms[0].code == '197433003'
    assert ehrtext.phrases[0].terms[0].description == 'pólipo de vesícula biliar'
    assert ehrtext.phrases[0].terms[0].text == 'polipos'
    assert len(ehrtext.phrases[0].terms[0].qualifiers) == 1
    assert ehrtext.phrases[0].terms[0].qualifiers[0].code == '63727002'
    assert ehrtext.phrases[0].terms[0].qualifiers[0].text == 'vesiculares'


def test_term_to_snomed():
    snomed_Term = snomed.SnomedTerm('38341003', 'hipertensión arterial', 'trastorno')
    ehrTerm = prediction.EHRTerm('hipertensión arterial', snomed_Term)
    assert ehrTerm.to_snomed == '38341003 |hipertensión arterial|'

    snomed_Term = snomed.SnomedTerm('75540009', 'elevado', 'calificador')
    ehrQualifier = prediction.EHRQualifier('elevado', snomed_Term)
    assert ehrQualifier.to_snomed == '75540009 |elevado|'


def test_term_with_qualifiers_to_snomed():
    qualifiers = []
    snomed_Term = snomed.SnomedTerm('75540009', 'elevado', 'calificador')
    qualifiers.append(prediction.EHRQualifier('elevada', snomed_Term))

    snomed_Term = snomed.SnomedTerm('255604002', 'leve', 'calificador')
    qualifiers.append(prediction.EHRQualifier('elevada', snomed_Term))

    snomed_Term = snomed.SnomedTerm('69480007', 'medición de gamma glutamil transferasa', 'procedimiento')
    ehrTerm = prediction.EHRTerm('ggt', snomed_Term, qualifiers)

    assert ehrTerm.to_snomed == '69480007 |medición de gamma glutamil transferasa| : (363713009 |tiene interpretación| = 75540009 |elevado|, 246112005 |severidad| = 255604002 |leve|)'


def test_term_with_qualifiers_to_snomed_2():
    qualifiers = []
    snomed_Term = snomed.SnomedTerm('410516002', 'se sabe que está ausente', 'calificador')
    qualifiers.append(prediction.EHRQualifier('sin', snomed_Term))

    snomed_Term = snomed.SnomedTerm('386661006', 'fiebre', 'hallazgo')
    ehrTerm = prediction.EHRTerm('fiebre', snomed_Term, qualifiers)

    assert ehrTerm.to_snomed == '386661006 |fiebre| : (408729009 |contexto de un hallazgo| = 410516002 |se sabe que está ausente|)'


def test_term_with_qualifiers_to_snomed_3():
    qualifiers = []
    snomed_Term = snomed.SnomedTerm('410513005', 'en el pasado', 'calificador')
    qualifiers.append(prediction.EHRQualifier('ap de', snomed_Term))

    snomed_Term = snomed.SnomedTerm('38341003', 'hipertensión arterial', 'trastorno')
    ehrTerm = prediction.EHRTerm('fiebre', snomed_Term, qualifiers)

    assert ehrTerm.to_snomed == '38341003 |hipertensión arterial| : (408731000 |contexto temporal| = 410513005 |en el pasado|)'


def test_term_with_qualifiers_to_snomed_4():
    qualifiers = []
    snomed_Term = snomed.SnomedTerm('361684008', 'columna vertebral cervical (como un todo)', 'estructura corporal')
    qualifiers.append(prediction.EHRQualifier('cervical', snomed_Term))

    snomed_Term = snomed.SnomedTerm('57048009', 'contractura', 'anomalía morfológica')
    ehrTerm = prediction.EHRTerm('contractura', snomed_Term, qualifiers)

    assert ehrTerm.to_snomed == '57048009 |contractura| : (363698007 |sitio del hallazgo| = 361684008 |columna vertebral cervical (como un todo)|)'


def test_term_with_qualifiers_to_snomed_5():
    qualifiers = []
    snomed_Term = snomed.SnomedTerm('444148008', 'persona en la familia del sujeto', 'persona')
    qualifiers.append(prediction.EHRQualifier('af de', snomed_Term))

    snomed_Term = snomed.SnomedTerm('38341003', 'hipertensión arterial', 'trastorno')
    ehrTerm = prediction.EHRTerm('hta', snomed_Term, qualifiers)

    assert ehrTerm.to_snomed == '38341003 |hipertensión arterial| : (408732007 |contexto de relación con el sujeto| = 444148008 |persona en la familia del sujeto|)'


def test_term_with_qualifiers_to_snomed_6():

    snomed_Term = snomed.SnomedTerm('38341003', 'hipertensión arterial', 'trastorno')
    ehrTerm1 = prediction.EHRTerm('hta', snomed_Term, [])

    qualifiers = []
    snomed_Term = snomed.SnomedTerm('28995006', 'tratado con', 'atributo')
    qualifiers.append(prediction.EHRQualifier('tto con', snomed_Term))

    snomed_Term = snomed.SnomedTerm('387458008', 'aspirina', 'sustancia')
    ehrTerm2 = prediction.EHRTerm('aspirina', snomed_Term, qualifiers)

    ehrTerm1.terms = [ehrTerm2]
    assert ehrTerm1.to_snomed == '38341003 |hipertensión arterial| : (28995006 |tratado con| = 387458008 |aspirina|)'


def test_phrase_to_snomed():

    snomed_term_1 = snomed.SnomedTerm('22253000', 'dolor', 'hallazgo')
    qualifier = snomed.SnomedTerm('255604002', 'leve', 'calificador')
    ehrTerm1 = prediction.EHRTerm('dolor', snomed_term_1, [qualifier])

    snomed_term_2 = snomed.SnomedTerm('302538001', 'brazo', 'estructura corporal')
    qualifier = snomed.SnomedTerm('24028007', 'derecho', 'calificador')
    ehrTerm2 = prediction.EHRTerm('brazo', snomed_term_2, [qualifier])

    snomed_term_3 = snomed.SnomedTerm('373265006', 'analgésico', 'producto medicinal')
    ehrTerm3 = prediction.EHRTerm('analgesicos', snomed_term_3, [])

    phrase = prediction.EHRPhrase('dolor de brazo tto con analgesicos', [ehrTerm2, ehrTerm1, ehrTerm3])

    assert phrase.main_term == ehrTerm1

    assert len(ehrTerm1.terms) == 2
    assert len(ehrTerm2.terms) == 0
    assert len(ehrTerm3.terms) == 0

    assert phrase.to_snomed == '22253000 |dolor| : (246112005 |severidad| = 255604002 |leve|, 363698007 |sitio del hallazgo| = 302538001 |brazo| : (272741003 |lateralidad| = 24028007 |derecho|), 47429007 |asociado con| = 373265006 |analgésico|)'


def test_phrase_to_snomed_2():

    snomed_term_1 = snomed.SnomedTerm('XXX', 'lesión', 'hallazgo')
    ehrTerm1 = prediction.EHRTerm('lesión', snomed_term_1, [])

    snomed_term_2 = snomed.SnomedTerm('YYY', 'fcc', 'procedimiento')
    ehrTerm2 = prediction.EHRTerm('fcc', snomed_term_2, [])

    phrase = prediction.EHRPhrase('lesión en fcc', [ehrTerm1, ehrTerm2])

    assert phrase.main_term == ehrTerm2


def test_to_doc():
    from nlp_service import NLPService
    snomed_term_1 = snomed.SnomedTerm('22253000', 'dolor', 'hallazgo')
    qualifier = snomed.SnomedTerm('255604002', 'leve', 'calificador')
    ehrTerm1 = prediction.EHRTerm('dolor', snomed_term_1, [qualifier])

    snomed_term_2 = snomed.SnomedTerm('302538001', 'brazo', 'estructura corporal')
    qualifier = snomed.SnomedTerm('24028007', 'derecho', 'calificador')
    ehrTerm2 = prediction.EHRTerm('brazo', snomed_term_2, [qualifier])

    snomed_term_3 = snomed.SnomedTerm('373265006', 'analgésico', 'producto medicinal')
    ehrTerm3 = prediction.EHRTerm('analgesicos', snomed_term_3, [])

    phrase = prediction.EHRPhrase('dolor de brazo tto con analgesicos', [ehrTerm2, ehrTerm1, ehrTerm3])
    pred = prediction.Prediction('dolor de brazo tto con analgesicos', 'dolor de brazo tto con analgesicos', [phrase])

    nlp = NLPService()
    doc = pred.to_doc(nlp.model.ner_phrases)

    assert doc is not None
    assert len(doc.ents) == 3
    assert doc.ents[0].label_ == '22253000'
    assert doc.ents[0].text == 'dolor'

    assert doc.ents[1].label_ == '302538001'
    assert doc.ents[1].text == 'brazo'

    assert doc.ents[2].label_ == '373265006'
    assert doc.ents[2].text == 'analgesicos'
