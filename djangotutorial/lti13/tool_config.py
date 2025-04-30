import json
import os


class PatchedToolConf:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self._config_data = self._load_config()

    def _load_config(self):
        with open(self.config_file_path, 'r') as f:
            return json.load(f)

    def get_auth_login_url(self, iss):
        return self._config_data.get(iss, {}).get('auth_login_url')

    def get_redirect_uri(self, request):
        iss = request.get_param('iss')
        return self._config_data.get(iss, {}).get('tool_redirect_url')

    def get_client_id(self, iss):
        return self._config_data.get(iss, {}).get('client_id')

    def get_jwk_config(self):
        return self._config_data.get('jwks_keys', {})

    def get_deployment_ids(self, iss):
        return self._config_data.get(iss, {}).get('deployment_ids', [])
