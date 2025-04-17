from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.message_launch import MessageLaunch
from .adapters import DjangoRequest
from .storage import DjangoSessionLaunchDataStorage
from django.views.decorators.csrf import csrf_exempt
import os
from .cookies import DjangoCookieService

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL_CONFIG_FILE = os.path.join(BASE_DIR, 'lti13', 'tool_config.json')

@csrf_exempt
def lti13_login(request):
    django_request = DjangoRequest(request)
    tool_conf = ToolConfJsonFile(TOOL_CONFIG_FILE)
    launch_data_storage = DjangoSessionLaunchDataStorage(request)

    cookie_service = DjangoCookieService(request)
    return MessageLaunch(
        django_request, tool_conf, launch_data_storage
    ).enable_check_cookies()\
     .set_cookie_service(cookie_service)\
     .get_redirect()

@csrf_exempt
def lti13_launch(request):
    django_request = DjangoRequest(request)  # 👈 This is crucial
    tool_conf = ToolConfJsonFile(TOOL_CONFIG_FILE)
    launch_data_storage = DjangoSessionLaunchDataStorage(request)
    cookie_service = DjangoCookieService(request)

    message_launch = MessageLaunch(
        django_request,
        tool_conf,
        launch_data_storage,
        cookie_service=cookie_service
    ).validate_registration().validate()

    # Get data from JWT
    data = message_launch.get_launch_data()

    request.session['user_id'] = data.get('sub')
    request.session['roles'] = data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
    request.session['name'] = data.get('name')

    return render(request, 'apiapp/practice.html', {
        'user_id': request.session.get('user_id'),
        'name': request.session.get('name'),
        'roles': request.session.get('roles'),
    })

from django.http import JsonResponse
import os
import json

def jwks_view(request):
    jwks_path = os.path.join(os.path.dirname(__file__), '.well-known', 'jwks.json')
    with open(jwks_path, 'r') as f:
        data = json.load(f)
    return JsonResponse(data)
