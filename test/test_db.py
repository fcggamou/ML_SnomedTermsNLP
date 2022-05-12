import prediction
from db import save_new_ehrtext_training_data
import db
import config
import json


def test_save():

    db.TRAINING_CONNECTION_STRING = config.sql_test_conn
    json_str = "{\"EHRPhrase\":[{\"EHRTextID\":0,\"expression\":\"polipos vesiculares\",\"Status\":null,\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"snomedCTExpression\":\"197433003 |pólipo de vesícula biliar| : (47429007 |asociado con| = 63727002 |vesicular|)\",\"EHRText\":null,\"User\":null,\"terms\":[{\"EHRTextID\":0,\"Phrase\":null,\"Text\":\"polipos\",\"TermCode\":\"197433003\",\"Status\":null,\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"EHRPhrase\":null,\"qualifiers\":[{\"EHRTextID\":0,\"Phrase\":null,\"Text\":null,\"TermCode\":null,\"QualifierCode\":\"63727002\",\"text\":\"vesiculares\",\"UserName\":null,\"Uptime\":\"0001-01-01T00:00:00\",\"EHRTerm\":null,\"snomedCTTerm\":{\"Code\":\"63727002\",\"Description\":\"vesicular\",\"Standard\":null,\"Domain\":\"calificador\",\"ParentCode\":null,\"Active\":null,\"Version\":null,\"EHRQualifier\":[],\"EHRTerm\":[],\"Qualifier\":null,\"Synonym\":[],\"Term1\":[],\"Term2\":null},\"User\":null,\"SnomedQualifier\":\"vesicular\"}],\"snomedCTTerm\":{\"Code\":\"197433003\",\"Description\":\"pólipo de vesícula biliar\",\"Standard\":null,\"Domain\":\"trastorno\",\"ParentCode\":null,\"Active\":null,\"Version\":null,\"EHRQualifier\":[],\"EHRTerm\":[],\"Qualifier\":null,\"Synonym\":[],\"Term1\":[],\"Term2\":null},\"User\":null,\"values\":[],\"Description\":\"pólipo de vesícula biliar\",\"Domain\":\"trastorno\"}]}],\"User\":null,\"ID\":1,\"Text\":\"polipos vesiculares.\",\"Type\":\"MotivoDeConsulta\",\"Speciality\":\"Medicina Interna\",\"Status\":\"Revisado\",\"UserName\":\"admin\",\"Uptime\":\"2021-04-06T10:15:44.1315811-03:00\"}"
    json_dic = json.loads(json_str)
    ehrtext = prediction.json_to_ehrtext(json_dic)
    save_new_ehrtext_training_data(ehrtext)
