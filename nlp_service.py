import os
from utils import load_from_file
import config
from model.model_factory import get_model


class NLPService():
    def __init__(self):
        self.model = get_model()
        self.load_spellchecker()

    def predict(self, text):
        prediction = self.model.predict(text)
        return prediction

    def predict_qualifier(self, text):
        return self.model.predict_qualifier(text)

    def load_spellchecker(self):
        if config.spellchecker_max_distance == 0:
            print('Spell checking disabled.')
            return

        self.spellchecker = load_from_file(os.path.join(config.models_path, config.spellchecker_dest, config.spellchecker_name))

    def validate_length(self, text) -> bool:
        return config.max_ehrtext_length <= 0 or len(text) <= config.max_ehrtext_length
