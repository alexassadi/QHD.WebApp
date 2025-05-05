from pylti1p3.launch_data_storage.base import LaunchDataStorage

class DjangoSessionLaunchDataStorage(LaunchDataStorage):
    def __init__(self, request):
        self._session = request.session

    def save_launch_data(self, launch_id, data):
        self._session[f"lti_launch_{launch_id}"] = data

    def get_launch_data(self, launch_id):
        return self._session.get(f"lti_launch_{launch_id}")

    def delete_launch_data(self, launch_id):
        if f"lti_launch_{launch_id}" in self._session:
            del self._session[f"lti_launch_{launch_id}"]

    def check_state_is_valid(self, state):
        return self._request.session.get("lti1p3_state") == state
