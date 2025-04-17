from django.shortcuts import render
from pylti.decorators import lti
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@lti(request='session', error=HttpResponseRedirect('/lti/error/'))
def lti_launch(request, lti):
    # Store LTI user info in session (already handled if using request='session')
    request.session['user_id'] = request.LTI.get('user_id')
    request.session['roles'] = request.LTI.get('roles')
    request.session['context_id'] = request.LTI.get('context_id')

    # Redirect to your tool in apiapp
    return HttpResponseRedirect('/apiapp/dashboard/')