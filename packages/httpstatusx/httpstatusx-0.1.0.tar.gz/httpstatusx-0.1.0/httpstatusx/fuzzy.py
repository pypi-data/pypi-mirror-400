from httpstatusx.data import HTTP_STATUS

def fuzzy_match(term: str):
    term = term.replace("_", "").lower()

    for key in HTTP_STATUS:
        if term in key.replace("_", ""):
            return key
    return None
