import enums
from model.ner_model import NERModel
from model.sim_model import SIMModel
from model.model import Model
import config


def get_model() -> Model:
    if config.model == enums.Model.NER:
        return NERModel(config.models_path, config.NER_Phrases_name, config.NER_Terms_name, config.NER_Qualifiers_name, config.NER_Values_name)
    elif config.model == enums.Model.SIMILARITY:
        return SIMModel(config.models_path, config.Sim_Model, config.Sim_Phrases_name, config.Sim_Terms_name, config.Sim_Embeddings, config.Sim_TermCodes, config.Sim_Qualifier_Embeddings, config.Sim_QualifierCodes, config.sim_threshold)
