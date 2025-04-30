from pylti1p3.message_launch import MessageLaunch
from pylti1p3.exception import LtiException
from urllib.parse import urlencode
import secrets


class PatchedMessageLaunch(MessageLaunch):
    def _get_request_param(self, key):
        return self._request.POST.get(key) or self._request.GET.get(key)

    def enable_check_cookies(self):
        self._enable_check_cookies = True
        return self

    def get_redirect(self):
        if not hasattr(self, '_cookie_service'):
            raise AssertionError("Cookie Service must be set")

        # 🔧 Define cookie prefix manually
        self._cookie_prefix = 'lti1p3_'  # or anything consistent

        state = self._generate_state()
        nonce = self._generate_nonce()

        self._cookie_service.set_cookie(self._cookie_prefix + 'state', state, max_age=300)
        self._cookie_service.set_cookie(self._cookie_prefix + 'nonce', nonce, max_age=300)

        auth_login_url = self._get_auth_login_url()
        if not auth_login_url:
            raise LtiException("Missing auth_login_url")

        params = self._build_auth_params(state=state, nonce=nonce)
        return self._redirect(f"{auth_login_url}?{urlencode(params)}")

    def _generate_state(self):
        return secrets.token_urlsafe(32)

    def _generate_nonce(self):
        return secrets.token_urlsafe(32)

    def _redirect(self, url):
        from django.http import HttpResponseRedirect
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
