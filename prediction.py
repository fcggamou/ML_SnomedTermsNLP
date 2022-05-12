from spacy.tokens import Doc
from snomed import Snomed, SnomedTerm
from typing import List
import json
import text_utils
import locale
import re
import train_utils


class EHRBase():
    def to_json(self) -> str:
        return json.dumps(self._to_json_dic(), indent=4)


class EHRValue(EHRBase):
    def __init__(self, text: str, value: float, unit: str, username: str = None, uptime: str = None):
        self.text = text
        self.value = value
        self.unit = unit
        self.username = username
        self.uptime = uptime


class EHRTerm(EHRBase):
    def __init__(self, text, snomed_term: SnomedTerm, qualifiers=[], values: List[float] = [], terms: List = [], username: str = None, uptime: str = None):
        self.text = text_utils.revert_separate_punct(text)
        self.code = snomed_term.code
        self.description = snomed_term.description
        self.domain = snomed_term.domain
        self.qualifiers = qualifiers
        self.values = values
        self.username = username
        self.uptime = uptime
        self.snomed_term = snomed_term
        self.terms = terms

    @property
    def to_snomed(self) -> str:

        attribute_pairs = []
        if len(self.qualifiers) > 0:
            for qualifier in self.qualifiers:
                attribute = Snomed.instance().get_attribute_for_pair(self, qualifier)
                if attribute is not None:
                    attribute_pairs.append('{} = {}'.format(attribute.to_snomed, qualifier.to_snomed))

        if len(self.terms) > 0:
            for term in self.terms:
                attribute = Snomed.instance().get_attribute_for_pair(self, term)
                if attribute is not None:
                    attribute_pairs.append('{} = {}'.format(attribute.to_snomed, term.to_snomed))

        if len(attribute_pairs) > 0:
            attribute_snomed = ', '.join(attribute_pairs)
            return '{} : ({})'.format(self.snomed_term.to_snomed, attribute_snomed)
        return self.snomed_term.to_snomed


class EHRQualifier(EHRBase):
    def __init__(self, text: str, snomed_term: SnomedTerm, username: str = None, uptime: str = None):
        self.text = text_utils.revert_separate_punct(text)
        self.code = snomed_term.code
        self.description = snomed_term.description
        self.domain = snomed_term.domain
        self.username = username
        self.uptime = uptime
        self.snomed_term = snomed_term

    @property
    def to_snomed(self) -> str:
        return self.snomed_term.to_snomed


class EHRPhrase(EHRBase):
    def __init__(self, text: str, terms: List[EHRTerm], username: str = None, uptime: str = None):
        self.text = text_utils.revert_separate_punct(text)
        self.terms = sorted(terms, key=lambda x: (x.domain == 'procedimiento', x.domain == 'hallazgo' or x.domain == 'trastorno'), reverse=True)
        self.username = username
        self.uptime = uptime
        self.main_term = None
        if len(self.terms) > 0:
            self.main_term = self.terms[0]
            self.main_term.terms = self.terms[1:]

    @property
    def to_snomed(self) -> str:
        if len(self.terms) == 0:
            return ''
        return self.main_term.to_snomed


class Prediction(EHRBase):
    def __init__(self, original_text: str, text: str, phrases: List[EHRPhrase]):
        self.text = text
        self.phrases = phrases
        self.original_text = original_text

    def to_doc(self, nlp) -> Doc:
        ents = []
        doc = nlp.make_doc(self.original_text)
        for phrase in self.phrases:
            for term in phrase.terms:
                for pos in [m.start() for m in re.finditer(re.escape(term.text), self.original_text)]:
                    if pos > -1:
                        ent = doc.char_span(pos, pos + len(term.text), label=term.code)
                        if ent is not None and not any([x for x in ents if train_utils.overlap((x.start_char, x.end_char), (ent.start_char, ent.end_char))]):
                            ents.append(ent)
        doc.ents = ents
        return doc


class EHRText():
    def __init__(self, text: str, ehrtextid: float, status: str, specialty: str, uptime: str, username: str, type: str, phrases: List[EHRPhrase]):
        self.text = text
        self.ehrtextid = ehrtextid
        self.status = status
        self.specialty = specialty
        self.uptime = uptime
        self.username = username
        self.type = type
        self.phrases = phrases


def doc_to_values(doc: Doc) -> List[EHRValue]:
    values = []
    for ent in doc.ents:
        try:
            decimal_char = locale.localeconv()['decimal_point']
            values.append(EHRValue(ent.text, float(ent.text.replace(',', decimal_char)), None))
        except Exception:
            continue
    return values


def doc_to_ehrqualifiers(doc: Doc) -> List[EHRQualifier]:
    predictions = []
    for ent in doc.ents:
        snomed_term = Snomed.instance().search_by_code(ent.label_)
        term = EHRQualifier(ent.text, snomed_term)
        predictions.append(term)
    return predictions


def doc_to_ehrterms(doc: Doc, qualifiers: List[EHRTerm] = None, values: List[EHRValue] = None) -> List[EHRTerm]:
    predictions = []
    for ent in doc.ents:
        snomed_term = Snomed.instance().search_by_code(ent.label_)
        term = EHRTerm(ent.text, snomed_term, qualifiers, values)
        if qualifiers is not None:
            text = term.text
            for qualifier in qualifiers:
                text = text_utils.replace_whole_word(text, qualifier.text, '', True).strip()
            term.text = text
        predictions.append(term)
    return predictions


def json_to_ehrtext(dic: dict):
    phrases = []
    for phrase in dic['EHRPhrase']:
        if any([x for x in phrases if x.text == phrase['expression']]):
            continue
        terms = []
        for term in phrase['terms']:
            if any([x for x in terms if x.text == term['Text']]):
                continue
            qualifiers = []
            values = []
            for qualifier in term['qualifiers']:
                snomed_qualifier = Snomed.instance().search_by_code(qualifier['QualifierCode'])
                qualifiers.append(EHRQualifier(qualifier['text'], snomed_qualifier, username=qualifier['UserName'], uptime=qualifier['Uptime']))
            for value in term['values']:
                values.append(EHRValue(value['Text'], value['Value'], value['Unit'], username=value['UserName'], uptime=value['Uptime']))
            snomed_term = Snomed.instance().search_by_code(term['TermCode'])
            terms.append(EHRTerm(term['Text'], snomed_term, qualifiers, values, username=term['UserName'], uptime=term['Uptime']))
        phrases.append(EHRPhrase(phrase['expression'], terms, username=phrase['UserName'], uptime=phrase['Uptime']))

    return EHRText(dic['Text'], dic['ID'], dic['Status'], dic['Speciality'], dic['Uptime'], dic['UserName'], dic['Type'], phrases)
