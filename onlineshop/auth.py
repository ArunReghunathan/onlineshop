from datetime import datetime, timedelta

import django
import jwt

from django.conf import settings

from rest_framework import authentication, exceptions
from rest_framework.permissions import BasePermission

from apis.models import User

authentication_header_prefix = 'Token'

def is_authenticated(user):
    if django.VERSION < (1, 10):
        return user.is_authenticated()
    return user.is_authenticated


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        request.user = None
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. Token string should not contain spaces. Do
            # not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, leeway=9)
            print("payload  : ", payload)
        except Exception as e:
            msg = 'Invalid authentication. Could not decode token.  ', e.message
            raise exceptions.AuthenticationFailed(msg)

        try:
            if payload['user_type'] == "user":
                user = User.objects.get(uuid=payload['id'])
                user.user_type = "user"
            else:
                msg = 'User type is not defined'
                raise exceptions.AuthenticationFailed(msg)

        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)
        user.is_authenticated = True
        return (user, token)


class AllowOnlyAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == "admin":
            return (request.user and is_authenticated(request.user))
        return False

class AllowStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type in ["admin", "staff"]:
            return (request.user and is_authenticated(request.user))
        return False



class create_and_edit_by_Admin(BasePermission):

    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return (request.user and is_authenticated(request.user))
        elif view.action in ["update", "create"]:
            if request.user.user_type in ["admin"]:
                return (request.user and is_authenticated(request.user))

        return False


class create_and_edit_by_Admin_and_staff(BasePermission):

    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return (request.user and is_authenticated(request.user))
        elif view.action in ["update", "create"]:
            if request.user.user_type in ["admin", "staff"]:
                return (request.user and is_authenticated(request.user))
        return False


class AllowRegister(BasePermission):
    def has_permission(self, request, view):
        return (request.user and is_authenticated(request.user)) or request.method in ["POST"]

class AllowGet(BasePermission):
    def has_permission(self, request, view):
        return (request.user and is_authenticated(request.user)) or request.method in ["GET"]


class AllowGetOrPost(BasePermission):
    def has_permission(self, request, view):
        return (request.user and is_authenticated(request.user)) or request.method in ["GET"] or request.method in ["POST"]


class IsAuthenticatedAndOption(BasePermission):
    def has_permission(self, request, view):
        return (request.user and is_authenticated(request.user)) or request.method in ["OPTIONS"]


def GenerateToken(id, usertype='user'):

    dt = datetime.now() + timedelta(days=1)
    token = jwt.encode({
        'id': id,
        'user_type': usertype,
        'exp': int(dt.strftime('%s'))
    }, settings.JWT_SECRET_KEY, algorithm='HS256')
    return token


def check_admin_or_same_user(request, idUser):

    if str(request.user.id) != str(idUser) and request.user.user_type not in ["admin", "staff"]:
        raise ValueError("403 Forbidden")


def check_same_user(request, idUser):

    if str(request.user.id) != str(idUser):
        raise ValueError("403 Forbidden")


# end