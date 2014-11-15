from urlparse import urlparse

from requests.adapters import BaseAdapter
from requests import Response

from .client import MajorDomoClient, SecureMajorDomoClient

class MajorDomoAdapter(BaseAdapter):


    def __init__(self, timeout=1.0, retries=3):
        super(MajorDomoAdapter, self).__init__()
        self.timeout = timeout
        self.retries = retries
        self._client = None

    def send(self, req, **kwargs):
        parsed = urlparse(req.url)
        cli = self.get_client(parsed.netloc)
        service = parsed.path[1:].encode('utf-8')
        if req.body:
            raw = cli.send(service, req.body.encode('utf-8'))
        else:
            raw = cli.send(service)
        resp = Response()
        resp.status_code = 200
        resp._content = ''.join(raw)
        return resp

    def get_client(self, netloc):
        if self._client is None:
            self._client = self._create_client(netloc)
        return self._client

    def close(self):
        import ipdb; ipdb.set_trace();
        raise NotImplementedError

    def _create_client(self, netloc):
        return MajorDomoClient(
            'tcp://' + netloc,
            timeout=self.timeout,
            retries=self.retries)


class SecureMajorDomoAdapter(MajorDomoAdapter):

    def __init__(self, client_key, server_key, *args, **kwargs):
        super(SecureMajorDomoAdapter, self).__init__(*args, **kwargs)
        self.client_key = client_key
        self.server_key = server_key

    def _create_client(self, netloc):
        return SecureMajorDomoClient(
            self.server_key, self.client_key,
            'tcp://' + netloc,
            timeout=self.timeout,
            retries=self.retries)
