import string
import regex as re


def preprocess_input_text(text):
    text = separate_punct(text)
    text = fix_tildes(text)
    text = fix_carriage_return(text)
    text = fix_double_spaces(text)
    text = text.lower()

    return text


def fix_carriage_return(s):
    return s.replace('\r', '')


def separate_punct(s):
    punct = re.escape(string.punctuation)
    patterns = [r'([a-zA-Z]+)([{}]+)([a-zA-Z]*)'.format(punct),
                r'([a-zA-Z]*)([{}]+)([a-zA-Z]+)'.format(punct)]
    for pattern in patterns:
        while re.search(pattern, s) is not None:
            s = re.sub(pattern, r'\1 \2 \3', s)
    punct_after_number_patterns = [r'(\d+[\.\,]\d+|\d+)([{}]$)'.format(punct)]
    for pattern in punct_after_number_patterns:
        while re.search(pattern, s) is not None:
            s = re.sub(pattern, r'\1', s)
    return s


def revert_separate_punct(text):
    punct = re.escape(string.punctuation)
    pattern = r'(\s)([{}]+)(\s)'.format(punct)
    text = re.sub(pattern, r'\2 ', text).strip()

    return text


def remove_punc(s, replace=''):
    for c in string.punctuation:
        s = s.replace(c, replace)
    return s


def replace_with_suggestion(s, spellchecker):
    for word in set(remove_punc(s, ' ').split()):
        if (len(word) > 3) and not any(i.isdigit() for i in word):
            suggestions = spellchecker.lookup(word, 3)
            if len(suggestions) > 0 and suggestions[0].distance > 0:
                s = s.replace(word, suggestions[0].term)
    return s


def fix_tildes(s):
    return s.replace('à', 'á').replace('è', 'é').replace('ì', 'í').replace('ò', 'ó').replace('ù', 'ú')


def remove_tildes(s):
    return s.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')


def fix_double_spaces(s):
    while('  ' in s):
        s = s.replace('  ', ' ')
    return s


def add_missing_tildes(s, spellchecker):
    words = s.split()
    i = 0
    for word in words:
        suggestions = spellchecker.suggest(word)
        if len(suggestions) > 0:
            suggestion = suggestions[0]
            if remove_tildes(suggestion) == word:
                words[i] = suggestion
        i = i + 1
    return ' '.join(words)


def replace_whole_word(text, word, replace, only_start_and_end=False):
    if only_start_and_end:
        text = re.sub(r'^\b' + word + r'\b', replace, text)
        return re.sub(r'\b' + word + r'\b$', replace, text)
    return re.sub(word + r'\b', replace, text)


def get_n_grams(text, n, m):
    text = text.split()
    n_grams = []
    for j in range(n, m + 1):
        n_grams.extend([' '.join(text[i:i + j]) for i in range(len(text) - j + 1)])
    return n_grams
