import re


def single_regex(text: str, pattern: str, label: str):
    """
    Extract first match of a regular expression pattern within a text
    """
    search_patern = re.compile(pattern)
    match = re.search(search_patern, text)
    if match:
        start = match.start()
        end = match.end()
        yield start, end, text[start:end], label


def regex_matches(text: str, pattern: str, label: str):
    """
    Extract all matches of a regular expression pattern within a text
    """
    search_patern = re.compile(pattern, flags=re.IGNORECASE)
    matches = re.finditer(search_patern, text)
    for match in matches:
        start = match.start()
        end = match.end()
        yield start, end, text[start:end], label


def string_match(text: str, substring: str, label: str):
    """
    Extract first match of a search sub string within a text
    """
    start = text.find(substring)
    if start != -1:
        end = start + len(substring)
        yield start, end, text[start:end], label


def string_matches(text: str, substring:str, label:str):
    """
    Extract all matches of a search sub string within a text
    """
    matches = re.finditer(substring, text)
    for match in matches:
        start = match.start()
        end = match.end()
        yield start, end, text[start: end], label

def keywords_searcher(text: str, keywords: str, label: str):
    """
    Annotate all keywords in text as label
    """
    kwds_list = keywords.split(',')
    for keyword in kwds_list:
        matches = re.finditer(keyword, text)
        for match in matches:
            start = match.start()
            end = match.end()
            yield start, end, keyword, label
