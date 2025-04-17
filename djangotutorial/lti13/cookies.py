from pylti1p3.cookie import CookieService

class DjangoCookieService(CookieService):
    def __init__(self, request, response=None):
        self._request = request
        self._response = response

    def get_cookie(self, key):
        return self._request.COOKIES.get(key)

    def set_cookie(self, key, value, max_age=None):
        if self._response:
            self._response.set_cookie(key, value, max_age=max_age)

    def delete_cookie(self, key):
        if self._response:
            self._response.delete_cookie(key)