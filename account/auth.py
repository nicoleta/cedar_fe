
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import available_attrs
from functools import wraps


def user_has_permission(user, **kwargs):
    for perm in perms:
        if not user.has_perm(perm):
            raise PermissionDenied
    return True

def user_is_staff(user, **kwargs):
    if not user.is_staff:
        raise PermissionDenied
    return True

def user_is_superuser(user, **kwargs):
    if not user.is_superuser:
        raise PermissionDenied
    return True

def user_is_advertiser(user, **kwargs):
    if kwargs.get('staff_ok') and (user.is_superuser or user.is_staff):
        return True
    if user.groups.filter(name__in=['advertisers', 'account_reps']).count() > 0:
        return True
    raise PermissionDenied

def user_has_model_access(user, **kwargs):

    if user.is_superuser or user.is_staff:
        return True

    if kwargs['model'].__name__ in ['Advertiser', 'Campaign']:
        return user_is_advertiser(user, staff_ok=False) # we already checked for staff

    raise PermissionDenied

########################################################################################
###################### DECORATORS ######################################################
########################################################################################

def staff_member_required():
    return user_passes_test(user_is_staff)

def superuser_required():
    return user_passes_test(user_is_superuser)

def advertiser_required(staff_ok=True):
    def test_func(user):
        kwargs = {'staff_ok': staff_ok}
        return user_is_advertiser(user, **kwargs)
    return user_passes_test(test_func)

def login_not_required(view_func):
    """
    Marks a view function as not requiring login (LoginRequiredMiddleware).
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.login_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
