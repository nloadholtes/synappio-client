import re
import json
from urlparse import urljoin

import funcsigs

from .connection import Connection
from .model import Model
from .swagger import SwaggerSpec

class API(object):

    def __init__(self, swagger_path, base_url=None, auth_header=None):
        self.spec = SwaggerSpec(swagger_path)
        if base_url is None:
            base_url = self.spec.basePath
        self.connection = Connection(base_url, auth_header)
        self.models = Models(self)
        self.rpc = RPCOperations(self)
        self.resources = Resources(self, base_url)

    def marshal(self, value):
        '''Convert value, possibly a Model object, to a primitive jsonable type'''
        if isinstance(value, Model):
            return value._state
        return value

    def unmarshal(self, value, spec):
        '''Convert a json-safe value into the spec'''
        ref = spec.get('$ref')
        if ref is not None:
            Model = self.models[ref]
            state = {}
            for pname, prop in Model.__meta__.properties:
                if pname in value:
                    state[pname] = self.unmarshal(value[pname])
                else:
                    state[pname] = prop.defaultValue
            return Model(_state=state)

        if spec.keys() == ['$ref']:
            Model = self.models[spec.value]

class Collection(object):

    def __init__(self):
        self._state = {}

    def __getattr__(self, name):
        try:
            return self._state[name]
        except:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._state[name]

    def __dir__(self):
        return list(self._state)

    def __repr__(self):
        result = [repr(self.__class__)]
        result += [
            '    {}: {}'.format(k, v)
            for k, v in self._state.items()]
        return '\n'.join(result)


class Models(Collection):

    def __init__(self, api):
        super(Models, self).__init__()
        self.api = api
        for model in api.spec.iter_models():
            self._state[model['id']] = Model.class_factory(api, model)


class Resources(Collection):
    re_route = re.compile(r'(\{[a-zA-Z][^\}]*\})')

    def __init__(self, api, base_url):
        super(Resources, self).__init__()
        self.api = api
        self.base_url = base_url
        self._path_patterns = []
        for apispec in api.spec.iter_apis():
            r = Resource.class_factory(api, apispec)
            path = r.__meta__['path']
            path_pattern = self.pattern_for(path)
            self._state[path] = r
            self._path_patterns.append((path_pattern, r))

    def pattern_for(self, path):
        '''Convert a swagger path spec to a url'''
        if not path.startswith('/'):
            path = '/' + path
        parts = self.re_route.split(path)
        pattern_parts = []
        for part in parts:
            if self.re_route.match(part):
                pattern_parts.append('(.*)')
            else:
                pattern_parts.append(re.escape(part))
        return re.compile(''.join(pattern_parts) + '$')

    def alias(self, path, alias):
        '''Gives a short alias to a given path'''
        self._state[alias] = res = self._state[path]
        res.__name__ = alias

    def lookup(self, href):
        if href.startswith(self.base_url):
            path = href[len(self.base_url):]
        else:
            path = href

        for pattern, ResourceClass in self._path_patterns:
            if pattern.match(path):
                return ResourceClass
        else:
            return Resource


class RPCOperations(Collection):

    def __init__(self, api):
        super(RPCOperations, self).__init__()
        for apispec in api.spec.iter_apis():
            for opspec in apispec['operations']:
                op = RPCOp(api, apispec['path'], opspec)
                self._state[opspec['nickname']] = op


class Resource(object):
    __slots__ = ('_state')

    @classmethod
    def class_factory(cls, api, apispec):
        meta = {
            'api': api,
            'apispec': apispec,
            'path': apispec['path']}
        dct = {'__meta__': meta, '__slots__': ()}
        for op in apispec['operations']:
            dct[op['method'].lower()] = api.rpc[op['nickname']]
        name = '{}<{}>'.format(cls.__name__, apispec['path'])
        return type(name, (cls,), dct)

    def __init__(self, state):
        self._state = state

    def __getattr__(self, name):
        return getattr(self._state, name)

    def __setattr__(self, name, value):
        if name == '_state':
            return super(Resource, self).__setattr__(name, value)
        return setattr(self._state, name, value)

    def __delattr__(self, name):
        if name == '_state':
            return super(Resource, self).__delattr__(name)
        return delattr(self._state, name)

    def __getitem__(self, name):
        try:
            return getattr(self._state, name)
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name, value):
        try:
            return setattr(self._state, name, value)
        except AttributeError:
            raise KeyError(name)

    def __delitem__(self, name):
        try:
            return delattr(self._state, name)
        except AttributeError:
            raise KeyError(name)

    @property
    def links(self):
        try:
            return self._state.meta.links
        except KeyError:
            return []

    @property
    def href(self):
        return self._state.meta.href

    def link(self, rel):
        for link in self.links:
            if link.rel == rel:
                if link.href.startswith('/'):
                    key = link.href
                else:
                    key = urljoin(self.href, link.href)
                return self.__meta__['api'].resources.lookup(key)

    def __repr__(self):
        return '{}: {}'.format(self.__meta__['path'], self._state)

    def __json__(self):
        return self._state.__json__()


class RPCOp(object):

    def __init__(self, api, path, opspec):
        self.api = api
        self.path = path
        self.opspec = opspec
        self.method = opspec['method']
        os_type = opspec.get('type')
        if os_type is None:
            self.type = None
        else:
            self.type = api.models[os_type]
        self.params = [RPCParam(pinfo) for pinfo in opspec['parameters']]
        self.signature = funcsigs.Signature(
            [p.func_param for p in self.params])
        self.__doc__ = opspec.get('summary')

    def __call__(self, *args, **kwargs):
        arguments = self.signature.bind(*args, **kwargs).arguments
        path_args = self.collect('path', arguments)
        query_args = self.collect('query', arguments)
        body = self.collect('body', arguments)
        request_args = dict(
            method=self.method,
            path=self.path.format(**path_args),
            params=query_args)
        if body is not None:
            request_args['data'] = json.dumps(body.__json__())
        res = self.api.connection.request(**request_args)
        if self.type is None:
            return None
        result_state = self.type(_state=res.json())
        if 'meta' in result_state:
            ResultResource = self.api.resources.lookup(result_state.meta.href)
        else:
            ResultResource = Resource
        return ResultResource(result_state)

    def __repr__(self):
        return '<{} {}>'.format(self.method, self.path)

    def collect(self, paramType, arguments):
        result = {}
        for param in self.params:
            if param.paramType == paramType:
                result[param.name] = arguments.get(param.py_name, param.defaultValue)
        if paramType == 'body':
            if result:
                return result['body']
            else:
                return None
        return result


class RPCParam(object):

    def __init__(self, pinfo):
        self.name = pinfo['name']
        self.py_name = pinfo['name'].replace('.', '_')
        self.defaultValue = pinfo.get('defaultValue')
        self.paramType = pinfo['paramType']
        func_param_kwargs = {}
        if 'defaultValue' in pinfo:
            func_param_kwargs['default'] = pinfo['defaultValue']
        self.func_param = funcsigs.Parameter(
            self.py_name,
            funcsigs.Parameter.POSITIONAL_OR_KEYWORD,
            **func_param_kwargs)
