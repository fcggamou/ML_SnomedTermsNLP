from model.model import Model
from prediction import Prediction, EHRPhrase, EHRTerm, EHRQualifier, EHRValue
from sentence_transformers import SentenceTransformer, util
import spacy
import os
import file_utils
import numpy as np
from snomed import Snomed
import config
import utils


class SIMModel(Model):
    def __init__(self, models_path, sim_name, ner_phrases_name, ner_terms_name, embeddings_name, termcodes_name, qualifier_embeddings_name, qualifiercodes_name, threshold):
        print("Loading terms similarity model...")
        self.sim = SentenceTransformer(os.path.join(models_path, sim_name))
        self.embeddings = file_utils.load_from_file(os.path.join(models_path, sim_name, embeddings_name))
        self.term_codes = file_utils.load_from_file(os.path.join(models_path, sim_name, termcodes_name))
        self.qualifier_embeddings = file_utils.load_from_file(os.path.join(models_path, sim_name, qualifier_embeddings_name))
        self.qualifier_codes = file_utils.load_from_file(os.path.join(models_path, sim_name, qualifiercodes_name))
        self.threshold = threshold

        if ner_phrases_name is not None:
            print('Loading phrases model...')
            self.ner_phrases = spacy.load(os.path.join(models_path, ner_phrases_name))
        else:
            self.ner_phrases = None

        if ner_terms_name is not None:
            print('Loading terms model...')
            self.ner_terms = spacy.load(os.path.join(models_path, ner_terms_name))
        else:
            self.ner_terms = None

    def predict(self, original_text) -> Prediction:
        text = self.preprocess(original_text)
        prediction_phrases = []
        phrases = self.ner_phrases(text).ents

        for pred_phrase in phrases:
            qualifiers = []
            values = []
            terms = []
            for phrase in pred_phrase.text.split("\n"):
                ents = self.ner_terms(phrase).ents

                for qualifier in [x for x in ents if x.label_ == 'Qualifier']:
                    snomed_term = self.get_similar([qualifier.text], self.qualifier_embeddings, self.qualifier_codes)[qualifier.text]
                    if snomed_term is not None:
                        qualifiers.append(EHRQualifier(qualifier.text, snomed_term))

                for value in [x for x in ents if x.label_ == 'Value']:
                    value_text = value.text.replace(',', config.decimal_char)
                    if utils.isfloat(value_text):
                        values.append(EHRValue(value.text, float(value_text), None))

                for term in [x for x in ents if x.label_ == 'Term']:
                    snomed_term = self.get_similar([term.text], self.embeddings, self.term_codes)[term.text]
                    if snomed_term is not None:
                        terms.append(EHRTerm(term.text, snomed_term, qualifiers, values))

                prediction_phrases.append(EHRPhrase(phrase, terms))

        return Prediction(original_text, text, prediction_phrases)

    def predict_qualifier(self, original_text) -> EHRQualifier:
        text = self.preprocess(original_text)
        qualifier_term = self.get_similar([text], self.qualifier_embeddings, self.qualifier_codes)[text]
        if qualifier_term is not None:
            return EHRQualifier(text, qualifier_term)

        return None

    def get_similar(self, texts, embeddings, codes) -> dict:
        res = {}
        if len(texts) == 0:
            return res
        texts_embeddings = self.sim.encode(texts, convert_to_tensor=True, normalize_embeddings=True)

        cos_sim = util.dot_score(texts_embeddings, embeddings)

        for text, c in zip(texts, cos_sim):
            candidate = int(np.argmax(c))
            confidence = c[candidate]
            if confidence > self.threshold:
                res[text] = Snomed.instance().search_by_code(codes[candidate])
            else:
                res[text] = None
        return res
