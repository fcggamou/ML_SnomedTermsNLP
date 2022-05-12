from spacy.scorer import Scorer
import train_utils
from train_utils import TrainSetGenerator
import train_data
from nlp_service import NLPService
from spacy.training import Example
import config


def evaluate(nlp: NLPService):

    print('Generating evaluation set...')
    df = train_data.sql_to_df('SELECT EHRText.Text, EHRTerm.Text as TermText, TermCode \
                               FROM EHRTerm JOIN EHRText ON EHRTextID = ID ')
    df.fillna("", inplace=True)

    df = TrainSetGenerator(0.1, ['Text', 'TermText']).get_train_set(df, 'TermText', 'Text', 'TermCode')
    train_docs = train_utils.train_set_to_docs(df)
    print('Evaluating...')
    
    predictions = []
    i = 0
    n = len(train_docs)
    for doc in train_docs:
        predictions.append(nlp.predict(doc.text).to_doc(nlp.model.ner_phrases))
        print("{:.1f}%".format(100 / (n - 1) * i), end='\r')
        i += 1

    examples = [Example(x, y) for (x, y) in zip(predictions, train_docs)]
    scores = Scorer(nlp.model.ner_terms).score(examples)
    print(scores)


if __name__ == '__main__':
    config.sim_threshold = 0.9
    config.Sim_Model = 'sim_big_mlm_aug_v2'
    # config.Sim_Qualifier_Embeddings = config.SIM_Test_Embeddings
    # config.Sim_QualifierCodes = config.SIM_Test_TermCodes
    # config.Sim_Embeddings = config.SIM_Test_Embeddings
    # config.Sim_TermCodes = config.SIM_Test_TermCodes
    nlp = NLPService()
    evaluate(nlp)
