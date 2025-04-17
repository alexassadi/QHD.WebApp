# lti13/storage.py

from pylti1p3.launch_data_storage.session import SessionLaunchDataStorage

class DjangoSessionLaunchDataStorage(SessionLaunchDataStorage):
    def __init__(self, request):
        self._session = request.session

    def save_launch_data(self, launch_id, data):
        self._session[f"lti_launch_{launch_id}"] = data

    def get_launch_data(self, launch_id):
        return self._session.get(f"lti_launch_{launch_id}")

    def delete_launch_data(self, launch_id):
        self._session.pop(f"lti_launch_{launch_id}", None)
