import json
from fastapi import HTTPException
from requests import HTTPError

# Convert HTTPError to fastapi.HTTPException
def construct(e: HTTPError):
    json_acceptable_string = str(e).replace("'", "\"")
    exception = json.loads(str(json_acceptable_string))
   
    status_code = exception['response']['status_code']
        
    if 'max_historical_days' in exception['response']:
        detail = exception['response']['max_historical_days']['summary']
    else:
        detail = exception['response']['detail']
        
    if not status_code:
        # If status code missing from HTTPError
        # returning 404 code HTTPStatus
        return HTTPException(
            status_code=404,
        )

    return HTTPException(
        status_code=status_code,
        detail=detail,  
    )
