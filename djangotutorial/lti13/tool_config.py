from pylti1p3.tool_config import ToolConfJsonFile


class PatchedToolConf(ToolConfJsonFile):
    def get_auth_login_url(self, iss):
        config = self._load_iss_config(iss)
        return config.get('auth_login_url')
