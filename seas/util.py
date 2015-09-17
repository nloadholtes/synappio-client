import re
import os
import sys
import string
import base64
import logging.config
import urlparse
import threading
import bson
import calendar
import time
import chardet
import requests
import pkg_resources

from datetime import datetime
from cStringIO import StringIO
from bag import csv2
import requests


TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
re_wildcard = re.compile(r'(\{[a-zA-Z][^\}]*\})')
re_newline = re.compile('(\r(?=[^\n]))|\r\n')
manager = pkg_resources.ResourceManager()


def restart_download(resp, offset):
    accept_ranges = resp.headers.get('accept-ranges', '').split(',')
    is_resumable = 'bytes' in accept_ranges
    new_req = resp.request.copy()
    sess = requests.Session()
    if is_resumable:
        new_req.headers['range'] = 'bytes={}-'.format(offset)
        new_resp = sess.send(new_req, stream=True)
        new_resp.raise_for_status()
        sess.close()
        return new_resp
    # Have to read/discard a bunch of data
    new_resp = sess.send(new_req, stream=True)
    new_resp.raise_for_status()
    bytes_discarded = 0
    while bytes_discarded < offset:
        to_read = min(8192, offset - bytes_discarded)
        chunk = new_resp.raw.read(to_read)
        bytes_discarded += len(chunk)
    return new_resp


def constant_time_compare(val1, val2):
    if len(val1) != len(val2):
        return False
    bits = 0
    for v1, v2 in zip(val1, val2):
        bits |= ord(v1) ^ ord(v2)
    return bits == 0


def setup_logging(config_file):
    '''Setup logging like pyramid.paster.setup_logging but does
    NOT disable existing loggers
    '''
    path = config_file.split('#')[0]
    full_path = os.path.abspath(path)
    here = os.path.dirname(full_path)
    return logging.config.fileConfig(
        full_path, dict(__file__=full_path, here=here),
        disable_existing_loggers=False)


def update_settings_from_environ(settings):
    for k, v in settings.items():
        if not isinstance(v, basestring):
            continue
        t = string.Template(v)
        v1 = t.safe_substitute(os.environ)
        settings[k] = v1


def extend_dict(dst, src):
    '''Perform a "deep" update of a dst dict with src.'''
    for src_k, src_v in src.items():
        dst_v = dst.get(src_k, None)
        if isinstance(dst_v, dict):
            extend_dict(dst_v, src_v)
        elif isinstance(dst_v, list):
            dst_v.extend(src_v)
        else:
            dst[src_k] = src_v


def strptime(s):
    'Return a datetime object from an iso formatted string'
    if '.' in s:
        s, us = s.split('.')
    else:
        us = '0'
    result = datetime.strptime(s, TIMESTAMP_FORMAT)
    return result.replace(microsecond=int(us))


def pattern_for(path):
    '''Convert a swagger path spec to a url'''
    if not path.startswith('/'):
        path = '/' + path
    parts = re_wildcard.split(path)
    pattern_parts = []
    for part in parts:
        if part.startswith('{'):
            name = part[1:-1]
            pattern_parts.append('(?P<{}>[^/]+)'.format(name))
        else:
            pattern_parts.append(re.escape(part))
    return re.compile(''.join(pattern_parts) + '$')


def actual_response_lines(resp):
    '''requests.Response.iter_lines() is BROKEN. It does not handle \r\n in
    as sane way. This generator does.
    '''
    cur_buf = ''
    for chunk in resp.iter_content(requests.models.ITER_CHUNK_SIZE):
        cur_buf += chunk
        cur_buf = re_newline.sub('\n', cur_buf)
        lines = cur_buf.split('\n')
        for line in lines[:-1]:
            yield line + '\n'
        cur_buf = lines[-1]
    if cur_buf:
        for line in cur_buf.split('\n'):
            yield line + '\n'



def really_unicode(s):
    # Try to guess the encoding
    def encodings():
        yield None
        yield 'utf-8'
        yield chardet.detect(s[:1024])['encoding']
        yield chardet.detect(s)['encoding']
        yield 'latin-1'
    return _attempt_encodings(s, encodings())


def load_content(url):
    '''Versatile text loader. Handles the following url types:

    http[s]://...
    file:///... (or just leave off the file://)
    egg://EggName/path
    '''
    parsed = urlparse.urlparse(url)
    if parsed.scheme == 'file://':
        assert not parsed.netloc, 'File urls must start with file:///'
        return open(parsed.path).read()
    if parsed.scheme == '':
        return open(parsed.path).read()
    elif parsed.scheme in ('http', 'https'):
        return requests.get(url).text
    elif parsed.scheme == 'egg':
        dist = pkg_resources.get_distribution(parsed.netloc)
        fn = dist.get_resource_filename(manager, parsed.path)
        return open(fn).read()
    else:
        assert False, "Don't know how to handle {} URLs".format(parsed.scheme)

def stripe_filter_factory(field, value):
    if field == 'fingerprint':
        return lambda x: x['card'][field] == value
    if field.endswith('_id'):
        field = 'id'
    return lambda x: x[field] == value

def daterange_filter_factory(before, after, ts_field='ts'):
    return lambda x: x[ts_field] >= after and x[ts_field] <= before

def timestamp_from_string(datestring, template='%Y-%m-%d'):
    if datestring:
        return calendar.timegm(time.strptime(datestring, '%Y-%m-%d'))

def datetime_from_string(datestring, template='%Y-%m-%d'):
    if datestring:
        return datetime.strptime(datestring, template)
    return None

def jsonify(obj, **json_kwargs):
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat() + 'Z'   #strftime(TIMESTAMP_FORMAT)
    elif hasattr(obj, '__json__'):
        return jsonify(obj.__json__(**json_kwargs))
    elif isinstance(obj, dict):
        return dict((k, jsonify(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return map(jsonify, obj)
    return obj


def chunk(iterator, chunksize):
    chunk = []
    iterator = iter(iterator)
    while True:
        try:
            chunk.append(iterator.next())
        except StopIteration:
            if chunk:
                yield chunk
            break
        if len(chunk) >= chunksize:
            yield chunk
            chunk = []


def csv_from_row_iter(it):
    sio = StringIO()
    wr = csv2.CsvWriter(sio)
    for row in it:
        sio.seek(0)
        sio.truncate()
        wr.put(row)
        yield sio.getvalue()


def nonce(size=48, encoding='base64url'):
    raw = os.urandom(size)
    if encoding == 'base64url':
        return base64.urlsafe_b64encode(raw).strip()
    else:
        return raw.encode(encoding).strip()

class Retrying(object):
    '''Class that retries its __call__() method n times on a given set of exceptions'''

    def __init__(self, retries, *exception_classes):
        self.retries = retries
        self.exception_classes = exception_classes

    def __call__(self, func, *args, **kwargs):
        for attempt in range(self.retries + 1):
            try:
                return func(*args, **kwargs)
            except self.exception_classes as err:
                info = sys.exc_info()
        raise info[0], info[1], info[2]


def _attempt_encodings(s, encodings):
    if s is None:
        return u''
    for enc in encodings:
        try:
            if enc is None:
                return unicode(s)  # try default encoding
            else:
                return unicode(s, enc)
        except (UnicodeDecodeError, LookupError):
            pass
    # Return the repr of the str -- should always be safe
    return unicode(repr(str(s)))[1:-1]


class BetterJoiningThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        self.result = None
        self.exc_info = None
        super(BetterJoiningThread, self).__init__(*args, **kwargs)

    def run(self):
        try:
            self.result = super(BetterJoiningThread, self).run()
        except Exception:
            self.exc_info = sys.exc_info()

    def join(self):
        super(BetterJoiningThread, self).join()
        if self.exc_info is not None:
            raise self.exc_info[0], self.exc_info[1], self.exc_info[2]
        return self.result

class CoreTranslator(object):

    def __init__(self, mapping):
        self.mapping = mapping

    def translate(self, response):
        if isinstance(response, basestring):
            for bad in self.mapping:
                response = re.sub(bad, self.mapping[bad], response)
        if isinstance(response, dict):
            response = {k:self.translate(response[k]) for k in response}
        if isinstance(response, list):
            response = [self.translate(i) for i in response]
        return response