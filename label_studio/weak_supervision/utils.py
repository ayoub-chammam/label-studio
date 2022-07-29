import spacy
from spacy.tokens import Doc

def get_latest_idx(cls):
    try:
        uid = cls.objects.latest('id').id
    except:
        uid = 0
    return uid

def get_keywords_from_content(text):
    keywords = [element.split(' ') for element in text.split(',')]
    tries = []
    for keyword in keywords:
        keyword = [token for token in keyword if token != '']
        tries.append(keyword)

    return tries

def get_lf_results(doc,lf_name):
    ents = doc.spans.get(lf_name)
    res = []
    for ent in ents:
        item = {"from_name": "label", "to_name": "text", "type": "labels", "value": {}}
        item['value'] = {"start": ent.start_char,
            "end": ent.end_char,
            "text": ent.text,
            "labels": [ent.label_]
            }
        res.append(item)
    return res