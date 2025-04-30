from pylti1p3.message_launch import MessageLaunch
from pylti1p3.exception import LtiException
from urllib.parse import urlencode


class PatchedMessageLaunch(MessageLaunch):
    def _get_request_param(self, key):
        return self._request.POST.get(key) or self._request.GET.get(key)

    def enable_check_cookies(self):
        self._enable_check_cookies = True
        return self

    def get_redirect(self):
        """
        This method performs the OpenID Connect redirect from the login initiation step.
        """
        state = self._generate_state()
        nonce = self._generate_nonce()

        self._cookie_service.set_cookie(self._cookie_prefix + 'state', state, max_age=300)
        self._cookie_service.set_cookie(self._cookie_prefix + 'nonce', nonce, max_age=300)

        redirect_url = self._get_auth_login_url()
        if not redirect_url:
            raise LtiException("Unable to build login URL: auth_login_url is missing")

        params = self._build_auth_params(state=state, nonce=nonce)
        return self._redirect(f"{redirect_url}?{urlencode(params)}")
