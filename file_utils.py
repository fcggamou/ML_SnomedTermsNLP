import pickle


def load_from_file(filename):
    with open(filename, "rb") as f:
        unpickler = pickle.Unpickler(f)
        data = unpickler.load()
    return data


def dump_to_file(object, filename):
    with open(filename, 'wb') as f:
        pickle.dump(object, f, protocol=4)


# EHRTextEHRTerms.pkl
# sql_to_pkl("SELECT Domain, TermCode, EHRTerm.text, EHRText.Text from EHRTerm JOIN Term on Term.code = EHRTerm.TermCode JOIN EHRText on EHRTerm.EHRTextID = EHRText.ID WHERE EHRText.Status='Revisado' or EHRText.Status='Inconsistente'", 'EHRTextEHRTerms.pkl')

# EHRQualifierText.pkl
# sql_to_pkl("SELECT QualifierCode, EHRTerm.Text, EHRText.Text FROM EHRTerm JOIN EHRText ON EHRTerm.EHRTextID=EHRText.ID LEFT OUTER JOIN EHRQualifier on EHRTerm.Text = EHRQUalifier.Text  and EHRTerm.EHRTextID = EHRQualifier.EHRTextID WHERE EHRText.Status='Revisado' or EHRText.Status='Inconsistente'", 'EHRQualifierText.pkl')

# Synonym.pkl
# sql_to_pkl('SELECT Domain, [Synonym].TermCode, Text, UserName, QualifierCode FROM [Synonym] JOIN Term on [Synonym].TermCode = Term.Code', 'Synonym.pkl')
