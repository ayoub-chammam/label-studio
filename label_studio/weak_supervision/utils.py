import spacy
from spacy.tokens import Doc
from skweak.gazetteers import Trie
from skweak.analysis import LFAnalysis
from .models import aggregation_model


def get_latest_idx(cls):
    try:
        uid = cls.objects.latest('id').id
    except:
        uid = 0
    return uid


def get_keywords_from_content(text, label):
    keywords = [element.split(' ') for element in text.split(',')]
    trie = []
    for keyword in keywords:
        keyword = [token for token in keyword if token != '']
        trie.append(keyword)
    tries = Trie()
    for item in trie:
        tries.add(item)
    tries = {label: tries}
    return tries
{'LOC': [
    ['Brooklyn'], ['', 'Chicago'], 
    ['', 'New', 'York'], ['', 'Miami'], ['', '', 'Georgia'], 
    ['', '', 'San', 'Francisco'], 
    ['', 'Los', 'Angeles'], ['', 'Jerusalem']]
    }

def get_lf_results(doc, lf_name):
    ents = doc.spans.get(lf_name)
    res = []
    for ent in ents:
        item = {"from_name": "label", "to_name": "text",
                "type": "labels", "value": {}}
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
        offset = (ent["value"]["start"], ent["value"]
                  ["end"], ent["value"]["labels"][0])
        gold_spans.append(offset)

    spans = [doc.char_span(x[0], x[1], label=x[2]) for x in gold_spans]
    doc.spans["gold"] = spans
    return doc

def get_gt_scores(docs, labels, gold='gold'):
    lf_analysis = LFAnalysis(docs, labels)
    gt_scores = lf_analysis.lf_empirical_scores(docs, gold_span_name=gold, gold_labels=labels)
    
    for annotator, label_dict in gt_scores.items():
        for label, metrics_dict in label_dict.items():
            res = {
                "annotator": annotator,
                "label": label,
                "precision": metrics_dict["precision"],
                "recall": metrics_dict["recall"],
                "f1": metrics_dict["f1"]
            }
            print(res)
            yield res


def get_weak_scores(docs, labels):
    lf_analysis = LFAnalysis(docs, labels)
    conflicts = lf_analysis.lf_conflicts()
    coverages = lf_analysis.lf_conflicts()
    overlaps = lf_analysis.lf_overlaps()

    for annotator, label_dict in overlaps.items():
        for label, _ in label_dict.items():
            res = {
                "annotator": annotator,
                "label": label,
                "overlaps": overlaps[annotator][label],
                "conflicts": conflicts[annotator][label],
                "coverage": coverages[annotator][label],
            }
            yield res


def get_scores(docs, labels):
    scores = get_weak_scores(docs, labels)
    if check_gold(docs):
        gold_scores = get_gt_scores(docs, labels)
        for score in scores:
            for gold_score in gold_scores:
                if score['annotator']==gold_score['annotator'] and score['label']==gold_score['label']:
                    score['precision'] = gold_score['precision']
                    score['recall'] = gold_score['recall']
                    score['f1'] = gold_score['f1']
                    print(score, '-')
            print(score, '1')
            yield score    
    # return scores
    
def lf_scores(docs, labels, lf_names):
    scores = get_scores(docs, labels)
    print(scores)
    # updated_scores = []
    for score in scores:
        if score['annotator'] in lf_names:
            # updated_scores.append(score)
            print(score, '2')
            yield score
    # return updated_scores

def model_scores(docs, labels, model_name):
    scores = get_scores(docs, labels)
    # model_scores = []
    for score in scores:
        if score['annotator'] == model_name:
            # model_scores.append(score)
            print(score, '3')
            yield score
    # return model_scores

def remove_gold(docs, weights):
    spans = list(docs[0].spans.data.keys())
    if 'gold' in spans:
        weights.update({'gold': 0})
    return weights


def check_gold(docs):
    spans = list(docs[0].spans.data.keys())
    return 'gold' in spans
