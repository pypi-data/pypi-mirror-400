from typing import Optional, Mapping, Any
from atk_common.enums.response_status_type_enum import ResponseStatusType
from atk_common.enums.api_error_type_enum import ApiErrorType

def create_response(
        status, 
        status_code, 
        response_msg, 
        http_headers: Optional[Mapping[str, str]]=None, 
        content_type='application/json', 
        api_error_type: Optional[ApiErrorType]=None):
    data = {}
    data['status'] = status
    data['statusCode'] = status_code
    data['responseMsg'] = response_msg
    data['httpHeaders'] = http_headers
    data['contentType'] = content_type
    if api_error_type is not None:
        data['apiErrorType'] = api_error_type
    else:
        data['apiErrorType'] = None
    return data

def is_response_ok(response):
    return response['status'] == ResponseStatusType.OK

def is_response_http(response):
    return response['status'] == ResponseStatusType.HTTP

def is_response_internal(response):
    return response['status'] == ResponseStatusType.INTERNAL
    
