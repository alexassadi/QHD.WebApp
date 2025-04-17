from pylti1p3.request import Request

class DjangoRequest(Request):
    def __init__(self, request):
        self._request = request

    def is_secure(self):
        return self._request.is_secure()

    def get_param(self, name):
        # This is the method that caused the NotImplementedError
        return self._request.POST.get(name) or self._request.GET.get(name)

    def get_cookie(self, name):
        return self._request.COOKIES.get(name)

    def get_header(self, name):
        return self._request.headers.get(name)

    def get_http_method(self):
        return self._request.method

    def get_body(self):
        return self._request.body

    def get_content_type(self):
        return self._request.content_type
