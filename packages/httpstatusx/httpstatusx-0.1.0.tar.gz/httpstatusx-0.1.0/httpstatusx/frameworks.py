def fastapistatusx(status_name: str, detail: str = None):
    from fastapi import HTTPException
    from httpstatusx import HTTP

    return HTTPException(
        status_code=HTTP[status_name],
        detail=detail or status_name.replace("_", " ")
    )

def flaskstatusx(status_name: str):
    from flask import abort
    from httpstatusx import HTTP

    abort(HTTP[status_name])
