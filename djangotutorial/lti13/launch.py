from pylti1p3.message_launch import MessageLaunch

class PatchedMessageLaunch(MessageLaunch):
    def _get_request_param(self, key):
        return self._request.POST.get(key) or self._request.GET.get(key)

    def enable_check_cookies(self):
        self._enable_check_cookies = True
        return self