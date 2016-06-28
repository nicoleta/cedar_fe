from re import compile as recompile
import json
from urlparse import parse_qs

from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from oauth20authentication import OAuth20Authentication, OAuthError
from account.models import AuthLog


class LoginRequiredMiddleware(object):
    """
    Middleware that requires a user to be authenticated to view any page on
    the site that hasn't been white listed. Exemptions to this requirement
    can optionally be specified in settings via a list of regular expressions
    in LOGIN_EXEMPT_URLS (which you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.

    Accounts OAuth access_token authentication.

    """
    EXEMPT_URLS = [recompile(str(settings.LOGIN_URL))]
    if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
        EXEMPT_URLS += [recompile(str(expr)) for expr in settings.LOGIN_EXEMPT_URLS]

    API_URLS = ['/api/']

    def return_api_forbidden(self, message=None):
        response = {"denied": "You do not have permission to access this resource. " + \
                              "You may need to login or otherwise authenticate the request."}
        if message:
            response.update({"detail": message})
        return HttpResponseForbidden(json.dumps(response))

    def return_need_auth(self, request, view, args, kwargs):
        if request.is_ajax():
            return self.return_api_forbidden()
        else:
            return login_required(view)(request, args, kwargs)

    def process_view(self, request, view, *args, **kwargs):
        if hasattr(request, 'user') and request.user.is_authenticated():
            pass  # user is logged in, no further checking required

        elif any(url in request.path_info for url in LoginRequiredMiddleware.API_URLS):

            # get the ip address for the authlog
            try:
                address = request.META['HTTP_X_FORWARDED_FOR']
            except KeyError:
                address = request.META['REMOTE_ADDR']
            # log the attempt
            authlog = AuthLog()
            authlog.ip_address = address
            authlog.requested_url = request.get_full_path()

            # api uses OAuth20
            try:
                if OAuth20Authentication().is_authenticated(request):
                    user = request.user
                    authlog.user = user
                    authlog.username = user.email
                    authlog.authenticated = True
                    authlog.save()
                else:
                    authlog.save()
                    return self.return_api_forbidden()
            except OAuthError as err:
                authlog.message = err
                authlog.save()
                return self.return_api_forbidden(message=err)

        elif hasattr(request, 'user') and not request.user.is_authenticated():
            if not (getattr(view, 'login_exempt', False) or
                    any(m.match(request.path_info) for m in LoginRequiredMiddleware.EXEMPT_URLS)):
                return self.return_need_auth(request, view, args, kwargs)
        elif not hasattr(request, 'user'):
            raise Exception("The Login Required middleware requires authentication middleware to be installed.")
