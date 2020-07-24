from rest_framework.views import exception_handler
import json
from rest_framework.response import Response

from django.core.serializers.json import DjangoJSONEncoder


class RequestLogMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, Response):
            # print(response.__dict__)
            if response.status_code < 300:
                # print(response)
                a = response.data
                response.data = {}
                response.data['response'] = a
                response.data['status'] = response.status_code
                response.data['message'] = ""
                response.content = json.dumps(response.data, cls=DjangoJSONEncoder)
            else:
                a = response.data
                response.data = {}
                response.data['response'] = a
                # response.data['message'] = response.data['response'].pop('message')
                response.data['status'] = response.status_code
                response.data['message'] = a.pop('detail')
                # try:
                #     response.data['message'] = a['detail']
                # except:
                #     response.data['message'] = response.data['response'].pop('message')

                response.content = json.dumps(response.data)
        return response


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        # response.data['status_code'] = response.status_code
        if not response.data.get('detail'):
            response.data['detail'] = "Validation Failed"
    return response
