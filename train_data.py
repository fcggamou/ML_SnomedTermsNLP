import file_utils
from config import sql_training_conn
import pandas as pd
import os


def sql_to_df(sql):
    import pyodbc
    conn = pyodbc.connect(sql_training_conn)
    return pd.read_sql(sql, conn)


def sql_to_pkl(sql, path):
    file_utils.dump_to_file(sql_to_df(sql), path)


def generate_training_data():

    sql_to_pkl("SELECT Phrase, EHRText.Text FROM EHRPhrase \
                          JOIN EHRText on EHRPhrase.EHRTextID = EHRText.ID \
                          WHERE EHRText.Status='Revisado'", os.path.join('data', 'training', 'EHRPhrase.pkl'))

    sql_to_pkl("SELECT EHRPhrase.Phrase, EHRTerm.Text, EHRTerm.TermCode FROM EHRPhrase \
                LEFT JOIN EHRTerm ON EHRPhrase.Phrase = EHRTerm.Phrase AND EHRPhrase.EHRTextID = EHRTerm.EHRTextID \
                JOIN EHRText on EHRPhrase.EHRTextID = EHRText.ID \
                WHERE EHRText.Status='Revisado'", os.path.join('data', 'training', 'EHRTerms.pkl'))

    sql_to_pkl("SELECT QualifierCode, EHRQualifier.QualifierText, EHRQualifier.Phrase, EHRQualifier.Text FROM EHRQualifier \
               JOIN EHRPhrase on EHRPhrase.EHRTextID = EHRQualifier.EHRTextID AND EHRPhrase.Phrase = EHRQualifier.Phrase \
               JOIN EHRText on EHRQualifier.EHRTextID = EHRText.ID \
               WHERE EHRText.Status='Revisado'", os.path.join('data', 'training', 'EHRQualifiers.pkl'))

    sql_to_pkl("SELECT Value, EHRValue.Text, EHRValue.Phrase FROM EHRValue \
            JOIN EHRPhrase on EHRPhrase.EHRTextID = EHRValue.EHRTextID AND EHRPhrase.Phrase = EHRValue.Phrase \
            JOIN EHRText on EHRValue.EHRTextID = EHRText.ID \
            WHERE EHRText.Status='Revisado'", os.path.join('data', 'training', 'EHRValue.pkl'))

    sql_to_pkl('select TermCode, EHRTerm.[Text] as TermText, EHRText.Text from [EHRPilot].dbo.EHRTerm \
                join [EHRPilot].dbo.EHRText on ehrterm.ehrtextid = ehrtext.ID \
                union \
                select TermCode, EHRTerm.[Text] as TermText, EHRText.Text from [Training].dbo.EHRTerm \
                join EHRText on ehrterm.ehrtextid=ehrtext.ID', os.path.join('data', 'training', 'EHRTermsOldAndNew.pkl'))

    sql_to_pkl('SELECT EHRTerm.Phrase, EHRTerm.Text, EHRTerm.TermCode, QualifierCode, QualifierText FROM EHRTerm \
                LEFT JOIN EHRQualifier \
                ON EHRTerm.EHRTextID = EHRQualifier.EHRTextID and EHRTerm.Text = EHRQualifier.Text', os.path.join('data', 'training', 'Relations.pkl'))

    sql_to_pkl('SELECT Text FROM EHRText', os.path.join('data', 'training', 'EHRText.pkl'))


if __name__ == '__main__':
    generate_training_data()
