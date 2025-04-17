from django.shortcuts import render
import json
from django.http import HttpResponseRedirect, HttpResponse
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.message_launch import MessageLaunch
from .adapters import DjangoRequest
from .storage import DjangoSessionLaunchDataStorage

TOOL_CONFIG_FILE = 'path/to/tool_config.json'

def lti13_login(request):
    django_request = DjangoRequest(request)
    tool_conf = ToolConfJsonFile(TOOL_CONFIG_FILE)
    launch_data_storage = DjangoSessionLaunchDataStorage(request)

    return MessageLaunch(django_request, tool_conf, launch_data_storage)\
        .enable_check_cookies()\
        .get_redirect()

def lti13_launch(request):
    django_request = DjangoRequest(request)
    tool_conf = ToolConfJsonFile(TOOL_CONFIG_FILE)
    launch_data_storage = DjangoSessionLaunchDataStorage(request)

    message_launch = MessageLaunch(django_request, tool_conf, launch_data_storage)
    data = message_launch.validate_registration().validate().get_launch_data()

    # Save user info
    request.session['user_id'] = data.get('sub')
    request.session['roles'] = data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
    request.session['name'] = data.get('name')

    return HttpResponseRedirect('/api/dashboard/')

