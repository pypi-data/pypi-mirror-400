# Data of the Status Codes

HTTP_STATUS = {
    # 1xx Informational
    "continue": 100,
    "switching_protocols": 101,
    "processing": 102,
    "early_hints": 103,

    # 2xx Success
    "ok": 200,
    "created": 201,
    "accepted": 202,
    "non_authoritative_information": 203,
    "no_content": 204,
    "reset_content": 205,
    "partial_content": 206,
    "multi_status": 207,
    "already_reported": 208,
    "im_used": 226,

    # 3xx Redirection
    "multiple_choices": 300,
    "moved_permanently": 301,
    "found": 302,
    "see_other": 303,
    "not_modified": 304,
    "temporary_redirect": 307,
    "permanent_redirect": 308,

    # 4xx Client Error
    "bad_request": 400,
    "unauthorized": 401,
    "payment_required": 402,
    "forbidden": 403,
    "not_found": 404,
    "method_not_allowed": 405,
    "not_acceptable": 406,
    "request_timeout": 408,
    "conflict": 409,
    "gone": 410,
    "unprocessable_entity": 422,
    "too_many_requests": 429,

    # 5xx Server Error
    "internal_server_error": 500,
    "not_implemented": 501,
    "bad_gateway": 502,
    "service_unavailable": 503,
    "gateway_timeout": 504,
    "http_version_not_supported": 505,
}

REVERSE_HTTP_STATUS = {v: k for k, v in HTTP_STATUS.items()}