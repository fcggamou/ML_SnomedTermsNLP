from config import sql_log_conn, sql_training_conn
import pyodbc
import datetime
from prediction import EHRText, EHRPhrase
from typing import List
import utils
TRAINING_CONNECTION_STRING = sql_training_conn
DEFAULT_USER_NAME = "Codical"


def log_request(text, response):
    conn = pyodbc.connect(sql_log_conn)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO RequestLog (Request, Response, Uptime) values (?, ?, ?)",
                   text, str(response), utils.datetime_to_sql(datetime.datetime.now()))
    conn.commit()


def save_new_ehrtext_training_data(ehrtext: EHRText) -> str:
    response = None
    try:
        conn = pyodbc.connect(TRAINING_CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.fast_executemany = True
        delete_ehrtext_training_data(cursor, ehrtext.ehrtextid)
        update_ehrtext(cursor, ehrtext)
        insert_phrases(cursor, ehrtext, ehrtext.phrases)
        conn.commit()
    except Exception as e:
        response = "Error: {}".format(str(e))
    return response


def insert_phrases(cursor, ehrtext: EHRText, phrases: List[EHRPhrase]):
    uptime = utils.json_date_to_sql(ehrtext.uptime)

    for phrase in phrases:
        cursor.execute("INSERT INTO EHRPhrase (EHRTextID, Phrase, Status, UserName, Uptime, SNOMEDCTExpression) VALUES (?, ?, ?, ?, ?, ?)", ehrtext.ehrtextid, phrase.text, ehrtext.status, phrase.username if phrase.username is not None else DEFAULT_USER_NAME, uptime, phrase.to_snomed)
        for term in phrase.terms:
            cursor.execute("INSERT INTO EHRTerm (EHRTextID, Phrase, Text, TermCode, Status, UserName, Uptime) VALUES (?, ?, ?, ?, ?, ?, ?)", ehrtext.ehrtextid, phrase.text, term.text, term.code, ehrtext.status, term.username if term.username is not None else DEFAULT_USER_NAME, uptime)
            for qualifier in term.qualifiers:
                cursor.execute("INSERT INTO EHRQualifier (EHRTextID, Phrase, Text, TermCode, QualifierCode, QualifierText, UserName, Uptime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ehrtext.ehrtextid, phrase.text, term.text, term.code, qualifier.code, qualifier.text, qualifier.username if qualifier.username is not None else DEFAULT_USER_NAME, uptime)
            i = 0
            for value in term.values:
                cursor.execute("INSERT INTO EHRValue (EHRTextID, Phrase, Text, TermCode, Index, Value, Unit, UserName, Uptime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ehrtext.ehrtextid, phrase.text, term.text, term.code, i, value.value, value.unit, value.username if value.username is not None else DEFAULT_USER_NAME, uptime)
                i += 1


def delete_ehrtext_training_data(cursor, ehrTextID: int):
    cursor.execute("DELETE FROM EHRQualifier WHERE EHRTextID = ?", ehrTextID)
    cursor.execute("DELETE FROM EHRValue WHERE EHRTextID = ?", ehrTextID)
    cursor.execute("DELETE FROM EHRTerm WHERE EHRTextID = ?", ehrTextID)
    cursor.execute("DELETE FROM EHRPhrase WHERE EHRTextID = ?", ehrTextID)


def update_ehrtext(cursor, ehrtext: EHRText):
    uptime = utils.json_date_to_sql(ehrtext.uptime)
    cursor.execute("UPDATE EHRText SET Status=?, UserName=?, UpTime=? WHERE ID = ?", ehrtext.status, ehrtext.username, uptime, ehrtext.ehrtextid)
