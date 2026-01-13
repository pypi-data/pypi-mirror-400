from atk_common.enums.api_error_type_enum import ApiErrorType
from atk_common.enums.response_status_type_enum import ResponseStatusType
from atk_common.utils.http_utils import is_http_status_internal, is_http_status_ok

def default_should_retry(message_status):
    if message_status.get('status') == ResponseStatusType.HTTP:
        status_code = message_status.get('statusCode')
        if is_http_status_ok(status_code):
            return False
        elif is_http_status_internal(status_code):
            if message_status.get('responseMsg') and message_status.get('responseMsg').get('errorType'):
                #errorType = 1: connection error => retry
                #errorType = 2: api internal error (database, etc) => do not retry
                if message_status.get('responseMsg').get('errorType') == ApiErrorType.CONNECTION.value:
                    return True
                else:
                    return False
            else:
                # Internal server error without errorType, do not retry
                return False
        else:
            # Other HTTP errors, retry            
            return True
    # Internal server error, do not retry
    return False
