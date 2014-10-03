import threading
import logging
from urlparse import urljoin

import requests

from seas.range import Range

log = logging.getLogger(__name__)


class Connection(object):
    _local = threading.local()

    def __init__(self, base_url, auth_header=None):
        self.base_url = base_url
        if auth_header:
            self.headers = {'Authorization': auth_header}
        else:
            self.headers = {}

    @property
    def session(self):
        sess = getattr(self._local, 'session', None)
        if sess is None:
            self._local.session = sess = requests.Session()
            sess.headers.update(self.headers)
        return sess

    def href(self, path):
        return self.base_url + path

    def request(self, method, path='', **kwargs):
        url = self.href(path)
        res = self.session.request(method, url, **kwargs)
        res.raise_for_status()
        return res

    def get(self, path='', **kwargs):
        return self.request('GET', path, **kwargs)

    def put(self, path='', **kwargs):
        return self.request('PUT', path, **kwargs)

    def post(self, path='', **kwargs):
        return self.request('POST', path, **kwargs)

    def delete(self, path='', **kwargs):
        return self.request('DELETE', path, **kwargs)

    def patch(self, path='', **kwargs):
        return self.request('PATCH', path, **kwargs)

    def options(self, path='', **kwargs):
        return self.request('OPTIONS', path, **kwargs)

    def get_paged(self, path='', **kwargs):
        kwargs = dict(kwargs)
        params = kwargs.setdefault('params', {})
        while True:
            result = self.get(path, **kwargs).json()
            paging = result['paging']
            items = result['items']
            for item in items:
                yield item
            if paging['skip'] + len(items) >= paging['total']:
                break
            else:
                params['paging.skip'] = paging['skip'] + paging['limit']

    def get_range_paged_lines(self, path='', range_type='bytes', **kwargs):
        skip = kwargs.pop('skip', 0)
        limit = kwargs.pop('limit', 50)
        total = skip + 1
        while skip < total:
            rng = Range('rows', skip=skip, limit=limit)
            headers = {'Range': rng.range_header}
            result = self.get(path, headers=headers, **kwargs)
            rng = Range.from_content_range(
                result.headers['Content-Range'])
            total = rng.total
            for row in result.iter_lines():
                yield row
            skip += rng.n

