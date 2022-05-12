from model.model import Model
from prediction import Prediction, EHRPhrase, doc_to_ehrterms, doc_to_ehrqualifiers, doc_to_values
import text_utils
import spacy
import os


class NERModel(Model):
    def __init__(self, models_path, ner_phrases_name, ner_terms_name, ner_qualifiers_name, ner_values_name):
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

        if ner_qualifiers_name is not None:
            print('Loading qualifiers model..')
            self.ner_qualifiers = spacy.load(os.path.join(models_path, ner_qualifiers_name))
        else:
            self.ner_qualifiers = None

        if ner_values_name is not None:
            print('Loading values model..')
            self.ner_values = spacy.load(os.path.join(models_path, ner_values_name))
        else:
            self.ner_values = None

    def predict(self, original_text) -> Prediction:
        text = self.preprocess(original_text)
        prediction_phrases = []
        for pred_phrase in self.ner_phrases(text).ents:
            for phrase in pred_phrase.text.split("\n"):
                qualifiers = doc_to_ehrqualifiers(self.ner_qualifiers(phrase)) if self.ner_qualifiers is not None else []
                values = doc_to_values(self.ner_values(text_utils.separate_punct(phrase))) if self.ner_values is not None else []
                terms = doc_to_ehrterms(self.ner_terms(phrase), qualifiers, values)
                prediction_phrases.append(EHRPhrase(phrase, terms))

        return Prediction(original_text, text, prediction_phrases)
