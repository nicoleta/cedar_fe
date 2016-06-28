
from tastypie.authorization import Authorization
from tastypie.test import ResourceTestCaseMixin
from tastypie.http import HttpForbidden
from tastypie.exceptions import ImmediateHttpResponse
from django.core.exceptions import PermissionDenied

from account import auth

UNAUTHORIZED_MESSAGE = "You are not authorized to access this resource."

class ApiAuthorization(Authorization):
    """
    OAuth2 authorization to be used by all API Resources
    """

    def __init__(self, model,
                       gen_kwargs_func=None,
                       filter_list_func=None,
                       auth_get_func=auth.user_is_staff,
                       auth_get_list_func=auth.user_is_staff,
                       auth_post_func=auth.user_is_staff,
                       auth_put_func=auth.user_is_staff,
                       auth_delete_func=auth.user_is_staff):
        """
        Init all the functions and kwargs that will be used to check different API actions.
        """
        self.model = model
        self.gen_kwargs_func = gen_kwargs_func
        self.filter_list_func = filter_list_func
        self.auth_get_func = auth_get_func
        self.auth_get_list_func = auth_get_list_func
        self.auth_post_func = auth_post_func
        self.auth_put_func = auth_put_func
        self.auth_delete_func = auth_delete_func

    def read_list(self, object_list, bundle):
        try:
            if self.gen_kwargs_func and len(object_list) > 0:
                kwargs = self.gen_kwargs_func(object_list[0].__dict__)
            else:
                kwargs = {}
            kwargs['model'] = self.model
            if self.filter_list_func:
                return self.filter_list_func(object_list, bundle.request.user)
            elif self.auth_get_list_func == None or self.auth_get_list_func(bundle.request.user, **kwargs):
                return object_list
        except PermissionDenied:
            raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def read_detail(self, object_list, bundle):
        try:
            if self.gen_kwargs_func:
                kwargs = self.gen_kwargs_func(bundle.obj.__dict__)
            else:
                kwargs = {}
            kwargs['model'] = self.model
            return self.auth_get_func == None or self.auth_get_func(bundle.request.user, **kwargs)
        except PermissionDenied:
            raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def create_list(self, object_list, bundle):
        raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def create_detail(self, object_list, bundle):
        try:
            if self.gen_kwargs_func:
                kwargs = self.gen_kwargs_func(bundle.data)
            else:
                kwargs = {}
            kwargs['model'] = self.model
            return self.auth_post_func == None or self.auth_post_func(bundle.request.user, **kwargs)
        except PermissionDenied:
            raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def update_list(self, object_list, bundle):
        raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def update_detail(self, object_list, bundle):
        try:
            if self.gen_kwargs_func:
                kwargs = self.gen_kwargs_func(bundle.obj.__dict__)
            else:
                kwargs = {}
            kwargs['model'] = self.model
            return self.auth_put_func == None or self.auth_put_func(bundle.request.user, **kwargs)
        except PermissionDenied:
            raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def delete_list(self, object_list, bundle):
        raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))

    def delete_detail(self, object_list, bundle):
        try:
            if self.gen_kwargs_func:
                kwargs = self.gen_kwargs_func(bundle.obj.__dict__)
            else:
                kwargs = {}
            kwargs['model'] = self.model
            return self.auth_delete_func == None or self.auth_delete_func(bundle.request.user, **kwargs)
        except PermissionDenied:
            raise ImmediateHttpResponse(HttpForbidden(UNAUTHORIZED_MESSAGE))



class ApiResourceTestCaseMixin(ResourceTestCaseMixin):
    """
    API tests should extend this because ResourceTestCaseMixin does not have a method for creating a OAuth2 client.
    """

    def create_oauth2(self, user):
        """
        Creates & returns the HTTP ``Authorization`` header for use with Oauth.
        """
        from provider.oauth2.models import Client, AccessToken

        try:
            client = Client.objects.get(user=user)
        except Client.DoesNotExist:
            client = Client(user=user, name="API custom tester", client_type=1, url="http://example.com")
            client.save()

        access_token = AccessToken.objects.create(
            user=user,
            client=client,
            scope= 1 << 1 | 1 << 2 #read + write
        )

        return 'OAuth %s' % access_token.token
