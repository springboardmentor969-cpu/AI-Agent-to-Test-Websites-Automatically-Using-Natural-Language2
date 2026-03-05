import spacy

nlp = spacy.load("en_core_web_sm")

def parse_instruction(text):

    doc = nlp(text)

    action = None
    target = None
    value = None

    for token in doc:

        if token.lemma_ in ["click","open","enter","type"]:
            action = token.lemma_

    if "'" in text:
        value = text.split("'")[1]

    for token in doc:

        if token.dep_ in ["dobj","pobj"]:
            target = token.text

    return {
        "action": action,
        "target": target,
        "value": value
    }