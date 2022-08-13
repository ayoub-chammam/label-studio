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

def gold_preds_to_spans(doc, gold_preds):
    gold_spans = []
    for ent in gold_preds:
        offset = (ent["value"]["start"], ent["value"]["end"], ent["value"]["labels"][0])
        gold_spans.append(offset)
    
    spans = [doc.char_span(x[0], x[1], label=x[2]) for x in gold_spans]
    doc.spans["gold"] = spans
    return doc

def scores_to_json(scores):
    for annotator, label_dict in scores.items():
        for label, metrics_dict in label_dict.items():
            res = {
                "annotator": annotator,
                "label": label,
                "precision": metrics_dict["precision"],
                "recall": metrics_dict["recall"],
                "f1": metrics_dict["f1"]
            }
            yield res

def remove_gold(docs, weights):
    spans = list(docs[0].spans.data.keys())
    if 'gold' in spans:
        weights.update({'gold':0})
    return weights

def check_gold(docs):
    spans = list(docs[0].spans.data.keys())
    return 'gold' in spans