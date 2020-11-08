import logging

from django.http.response import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import is_client_error, HTTP_200_OK


class ErrorResponse(Response):
    def __init__(self, message=None, code=HTTP_200_OK, payload=None, etype=None, status_code=666,
                 template_name=None, headers=None, exception=False, content_type=None):
        error = dict(message=message, code=code)
        data = dict(success=False, error=error)

        super(ErrorResponse, self).__init__(data=data, status=code, template_name=template_name,
                                            headers=headers, exception=exception, content_type=content_type)

def get_message(exc):
    message = getattr(exc, 'message', None)
    if not message:
        message = getattr(exc, 'DETAIL', str(exc))
        print("==============================================")
        print( exc)
        print( type(exc))


    return message


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django Rest Framework that adds
    the `status_code` to the response and renames the `detail` key to `error`.
    """

    if exc.__class__.__name__ == 'DoesNotExist':
        code = status.HTTP_404_NOT_FOUND
        message = get_message(exc)

    elif exc.__class__.__name__ == 'Http404':
        code = status.HTTP_404_NOT_FOUND
        message = "Does Not Exist"

    elif exc.__class__.__name__ in ['KeyError', 'MultiValueDictKeyError', 'AttributeError']:
        code = status.HTTP_400_BAD_REQUEST
        message = 'Bad request must pass: {}'.format(get_message(exc))

    elif exc.__class__.__name__ == 'ValidationError':
        code = status.HTTP_400_BAD_REQUEST
        message = get_message(exc)

    # elif exc.__class__.__name__ == 'IntegrityError':
    #     code = status.HTTP_400_BAD_REQUEST
    #     message =  get_message(exc)

    elif exc.__class__.__name__ == 'error':
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = get_message(exc)


    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = get_message(exc)

    response = ErrorResponse(message=message, code=code, status_code=400, content_type='application/json')
    return response
