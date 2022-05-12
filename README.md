# Codical
Transformers powered REST API for encoding EHRs into SNOMED-CT medical standard terms.

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/-vInBSSw4zY/0.jpg)](https://www.youtube.com/watch?v=-vInBSSw4zY)

- Encode arbitrarely long EHR written in natural language into [SNOMED-CT](https://en.wikipedia.org/wiki/SNOMED_CT) formal concept model [expressions](https://confluence.ihtsdotools.org/display/DOCSTART/7.+SNOMED+CT+Expressions#:~:text=SNOMED%20CT%20expressions%20are%20a,manner%2C%20which%20is%20automatically%20processable.).
- Identify terms and relations between them, including qualifiers, observable entities, body structures, findings, substances, numeric values and more.
- Achieved 0.91+ F1-Score on novel spanish EHR texts from a variety of medical specialties.
- [Transformer](https://arxiv.org/abs/1706.03762) based State Of The Art [Semantic Textual Similarity](https://www.sbert.net/docs/usage/semantic_textual_similarity.html)
- Transformer based terms relation extractor.
- Powerful State of the Art transformer based model allows for correctly encoding terms even containing typos, acronyms or abbreviations.
- Fully exposed as REST API.
