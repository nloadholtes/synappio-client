import logging

import jwt

from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.security import Authenticated, Everyone


log = logging.getLogger(__name__)


class JWTAuthenticationPolicy(CallbackAuthenticationPolicy):

    def __init__(self, secret):
        self.secret = secret

    def unauthenticated_userid(self, request):
        header = request.headers.get('Authorization', None)
        request.claims = dict(sub='', grp='')
        if header is None:
            return None
        try:
            bearer, data = header.split(' ')
            if bearer.lower() != 'bearer':
                return
            claims = jwt.decode(data, self.secret, leeway=5)
            request.claims = claims
            return claims['sub']
        except Exception as err:
            log.exception('Error getting jwt from %s: %s', header, err)
            return None

    def callback(self, userid, request):
        groups = request.claims['grp'].split(' ')
        groups = ['group:' + g for g in groups]
        result = ['account:' + userid] + groups
        result.append(Authenticated)
        result.append(Everyone)
        return result

    def remember(self, request, principal, **kw):  # pragma no cover
        return []

    def forget(self, request):  # pragma no cover
        return []
