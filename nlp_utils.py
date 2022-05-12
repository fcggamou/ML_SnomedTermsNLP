import config


def spellcheck(spellchecker, text):
    suggestions = spellchecker.lookup_compound(text, config.spellchecker_max_distance)
    if len(suggestions) > 0:
        return suggestions[0].term
    return None
