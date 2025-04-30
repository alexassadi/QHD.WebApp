from pylti1p3.message_launch import MessageLaunch
from pylti1p3.exception import LtiException
from urllib.parse import urlencode
from django.http import HttpResponseRedirect
import secrets


class PatchedMessageLaunch(MessageLaunch):
    def __init__(self, request, tool_conf, launch_data_storage, cookie_service=None):
        super().__init__(request, tool_conf, launch_data_storage, cookie_service=cookie_service)
        self._request = request
        self._tool_conf = tool_conf
        self._launch_data_storage = launch_data_storage
        self._cookie_service = cookie_service
        self._cookie_prefix = 'lti1p3_'  # Default for storing state/nonce

    def _get_request_param(self, key):
        return self._request.POST.get(key) or self._request.GET.get(key)

    def enable_check_cookies(self):
        self._enable_check_cookies = True
        return self

    def get_redirect(self):
        if not self._cookie_service:
            raise AssertionError("Cookie Service must be set")

        state = self._generate_state()
        nonce = self._generate_nonce()

        self._cookie_service.set_cookie(self._cookie_prefix + 'state', state, max_age=300)
        self._cookie_service.set_cookie(self._cookie_prefix + 'nonce', nonce, max_age=300)

        auth_login_url = self._get_auth_login_url()
        if not auth_login_url:
            raise LtiException("Missing auth_login_url")

        params = self._build_auth_params(state=state, nonce=nonce)
        return self._redirect(f"{auth_login_url}?{urlencode(params)}")

    def _get_auth_login_url(self):
        iss = self._request.get_param('iss')
        if not iss:
            raise LtiException('Missing "iss" parameter')
        return self._tool_conf.get_auth_login_url(iss)

    def _generate_state(self):
        return secrets.token_urlsafe(32)

    def _generate_nonce(self):
        return secrets.token_urlsafe(32)

    def _redirect(self, url):
        return HttpResponseRedirect(url)

    def _build_auth_params(self, state, nonce):
        return {
            'scope': 'openid',
            'response_type': 'id_token',
            'client_id': self.get_client_id(),
            'redirect_uri': self._tool_conf.get_redirect_uri(self._request),
            'login_hint': self._request.get_param('login_hint'),
            'response_mode': 'form_post',
            'nonce': nonce,
            'prompt': 'none',
            'state': state,
            'lti_message_hint': self._request.get_param('lti_message_hint')
        }
