import re


class Range(object):
    attrs = ('begin', 'end', 'total')
    _re_range = re.compile(
        r'([a-z]+) *= *(\d+) *- *(\d*)', flags=re.I)
    _re_content_range = re.compile(
        r'([a-z]+) *= *(\d+) *- *(\d*) */ *(\d+|\*)', flags=re.I)

    def __init__(self, range_unit='items', **kwargs):
        self.range_unit = range_unit
        self.begin = 0
        self.end = None
        self.total = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Range {}>'.format(
            self.content_range_header)

    @classmethod
    def from_range(cls, hdr):
        if hdr is None:
            return None
        m = cls._re_range.match(hdr)
        if m is None:
            return None
        if m.group(3):
            end = int(m.group(3))
        else:
            end = None
        return cls(
            range_unit=m.group(1),
            begin=int(m.group(2)),
            end=end)

    @classmethod
    def from_content_range(cls, hdr):
        m = cls._re_content_range.match(hdr)
        if m is None:
            return None
        if m.group(3):
            end = int(m.group(3))
        else:
            end = None
        if m.group(4) == '*':
            total = None
        else:
            total = int(m.group(4))
        return cls(
            range_unit=m.group(1),
            begin=int(m.group(2)),
            end=end,
            total=total)

    @property
    def range_header(self):
        return '{}={}-{}'.format(
            self.range_unit,
            self._maybe(self.begin, none=0),
            self._maybe(self.end, none=''))

    @property
    def content_range_header(self):
        return '{}={}-{}/{}'.format(
            self.range_unit,
            self._maybe(self.begin, none=0),
            self._maybe(self.end, none='*'),
            self._maybe(self.total, none='*'))

    @property
    def skip(self):
        return self.begin
    @skip.setter
    def skip(self, value):
        self.begin = value

    @property
    def limit(self):
        return self.end - self.begin + 1
    @limit.setter
    def limit(self, value):
        self.end = self.begin + value - 1

    @property
    def n(self):
        return self.end - self.begin + 1

    @property
    def paging(self):
        paging = dict(skip=self.skip, limit=self.limit)
        if self.total is not None:
            paging['total'] = self.total
        return paging

    def paginate_query(self, q):
        self.total = q.count()
        if self.skip:
            q = q.skip(self.skip)
        if self.end is not None:
            q = q.limit(self.limit)
        return q

    def _maybe(self, x, none=''):
        if x is None:
            return ''
        else:
            return x
