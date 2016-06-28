
import json

from django.shortcuts import render
from django.http import HttpResponse

from provider.oauth2.models import Client
from django.contrib.auth.models import User

from account.auth import staff_member_required, login_not_required

# add this decorator back when we have the login
#@staff_member_required()
@login_not_required
def create_oauth2_client(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse(content=json.dumps({'error': 'Missing user_id GET param.'}), content_type="application/json")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse(content=json.dumps({'error': 'User ID not found.'}), content_type="application/json")
    try:
        client = Client.objects.get(user=user)
        existing = True
    except Client.DoesNotExist:
        client = Client(user=user,
                        name="API Client",
                        client_type=1,
                        url="http://todo.com")
        client.save()
        existing = False
    return HttpResponse(content=json.dumps({'client_id': client.client_id, 'client_secret': client.client_secret,
                                            'existing': existing}),
                        content_type="application/json")
