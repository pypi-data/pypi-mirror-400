from httpstatusx.data import HTTP_STATUS, REVERSE_HTTP_STATUS
from httpstatusx.fuzzy import fuzzy_match

class HTTPDict:
    """Semantic HTTP status handler"""

    def __getitem__(self, key: str) -> int:
        key = key.lower().replace(" ", "_")
        if key in HTTP_STATUS:
            return HTTP_STATUS[key]

        match = fuzzy_match(key)
        if match:
            return HTTP_STATUS[match]

        raise KeyError(f"No HTTP status for '{key}'")

    def code(self, name: str) -> int:
        return self[name]

    def name(self, code: int) -> str:
        if code in REVERSE_HTTP_STATUS:
            return REVERSE_HTTP_STATUS[code]
        raise ValueError("Invalid HTTP status code")

    def category(self, code: int) -> str:
        if 100 <= code < 200:
            return "informational"
        if 200 <= code < 300:
            return "success"
        if 300 <= code < 400:
            return "redirection"
        if 400 <= code < 500:
            return "client_error"
        if 500 <= code < 600:
            return "server_error"
        return "unknown"

    def is_error(self, code: int) -> bool:
        return code >= 400

HTTP = HTTPDict()
