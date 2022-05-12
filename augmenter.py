def get_synonyms_for_term(term_code, terms, synonyms):
    descriptions = [terms.loc[term_code]['Description']]
    descriptions.extend(synonyms[synonyms['TermCode'] == term_code]['Text'].values)
    return descriptions


def create_qualifier_examples(df, terms, synonyms, cutoff, n=10):
    count = df.groupby(by='QualifierCode').agg('count')
    all_qualifier_codes = list(set(df['QualifierCode']))
    qualifier_codes_few_samples = list(set(count[count['QualifierText'] < cutoff].index.values))
    for qualifier_code in all_qualifier_codes:
        if qualifier_code in qualifier_codes_few_samples:
            for qualifier_synonym in get_synonyms_for_term(qualifier_code, terms, synonyms):
                for _, sample in df.sample(n).iterrows():
                    new_example = sample.copy()
                    new_example['QualifierCode'] = qualifier_code
                    new_example['Phrase'] = new_example['Phrase'].replace(new_example['QualifierText'], qualifier_synonym)
                    new_example['QualifierText'] = qualifier_synonym
                    df = df.append(new_example)

            new_example = sample.copy()
            new_example['QualifierCode'] = qualifier_code
            new_example['Phrase'] = qualifier_synonym
            new_example['QualifierText'] = qualifier_synonym
            new_example['Text'] = qualifier_synonym
            df = df.append(new_example)

        one_sample = df[df['QualifierCode'] == qualifier_code].sample(1).iloc[0]['QualifierText']
        new_example = sample.copy()
        new_example['QualifierCode'] = qualifier_code
        new_example['Phrase'] = one_sample
        new_example['QualifierText'] = one_sample
        new_example['Text'] = qualifier_synonym
        df = df.append(new_example)

    return df


def create_qualifier_negative_examples(df, ehrTerms):
    negative_examples = ehrTerms[~ehrTerms['Phrase'].isin(df['Phrase'])]
    for _, example in negative_examples.iterrows():
        new_example = df.iloc[0].copy()
        new_example['QualifierCode'] = ''
        new_example['Phrase'] = example['Phrase']
        new_example['QualifierText'] = ''
        new_example['Text'] = example['Phrase']
        df = df.append(new_example)
    return df


def create_negative_examples(df, terms, synonyms, entity_column, text_column, label_column, frac):
    term_codes = list(set(df[label_column].values))
    n = int(len(df) * frac)
    not_coded_terms = terms.loc[~terms.index.isin(term_codes)].sample(n)

    for code, term in not_coded_terms.iterrows():
        new_example = df.iloc[0].copy()
        new_example[text_column] = term['Description']
        new_example[entity_column] = term['Description']
        new_example[label_column] = 'UNK'
        df = df.append(new_example)
    return df


def create_synonym_examples(df, terms, synonyms, entity_column, text_column, label_column, n=5):
    term_codes = list(set(df[label_column].values))
    if '' in term_codes:
        term_codes.remove('')
    new_examples = []

    g = df.groupby(text_column).size()
    phrases = g[g == 1].index.values
    valid_samples = df[(df[entity_column] != '') & (df[text_column].isin(phrases))]

    for term_code in term_codes:
        for synonym in get_synonyms_for_term(term_code, terms, synonyms):
            for _, sample in valid_samples.sample(n).iterrows():
                new_example = sample.copy()
                new_example[text_column] = synonym
                new_example[entity_column] = synonym
                new_example[label_column] = term_code
                new_examples.append(new_example)
    return df.append(new_examples)
