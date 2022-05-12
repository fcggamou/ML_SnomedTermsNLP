import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from prediction import Prediction, EHRQualifier, doc_to_ehrqualifiers
import text_utils


class Model():
    def __init__(self):
        pass

    def predict(self, text) -> Prediction:
        pass

    def preprocess(self, text) -> str:
        return text_utils.preprocess_input_text(text)

    def predict_qualifier(self, original_text) -> EHRQualifier:
        text = self.preprocess(original_text)
        qualifiers = doc_to_ehrqualifiers(self.ner_qualifiers(text))
        if len(qualifiers) > 0:
            return qualifiers[0]

        return None
