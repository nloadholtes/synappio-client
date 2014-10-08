import json
from urlparse import urljoin

import funcsigs

from .connection import Connection
from .model import Model, Meta, ModelMeta, Unset
from .swagger import SwaggerSpec
from .util import pattern_for, jsonify

class API(object):

    def __init__(self, swagger_path, base_url=None, auth_header=None):
        self.swagger_path = swagger_path
        self.base_url = base_url
        self.auth_header = auth_header
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
            for pname, prop in Meta.get(Model).properties.items():
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
            self._state[model['id']] = ModelMeta.model_factory(api, model)


class Resources(Collection):

    def __init__(self, api, base_url):
        super(Resources, self).__init__()
        self.api = api
        self.base_url = base_url
        self._items = []
        for apispec in api.spec.iter_apis():
            r = ResourceMeta.resource_factory(api, apispec)
            path = Meta.get(r).path
            self._state[path] = r
            self._items.append(r)

    def alias(self, path, alias):
        '''Gives a short alias to a given path'''
        self._state[alias] = res = self._state[path]
        res.__name__ = alias

    def lookup(self, href):
        if href.startswith(self.base_url):
            path = href[len(self.base_url):]
        else:
            path = href

        matches = []
        for ResourceClass in self._items:
            pattern = Meta.get(ResourceClass).path_pattern
            match = pattern.match(path)
            if match:
                matches.append(ResourceClass)
        if len(matches) > 1:
            import ipdb; ipdb.set_trace();
        if matches:
            return matches[0]

    def resource_for(self, model):
        '''Try to make a model into a resource'''
        if 'meta' in model:
            cls = self.lookup(model.meta.href)
            if cls:
                return cls(model)
        return None


class RPCOperations(Collection):

    def __init__(self, api):
        super(RPCOperations, self).__init__()
        for apispec in api.spec.iter_apis():
            for opspec in apispec['operations']:
                op = RPCOp(api, apispec['path'], opspec)
                self._state[opspec['nickname']] = op


class ResourceMeta(Meta):

    def __init__(self, api, apispec):
        self.api = api
        self._apispec = Unset
        self.path = Unset
        self.path_pattern = Unset
        self.operations = Unset
        self.apispec = apispec

    @property
    def apispec(self):
        return self._apispec
    @apispec.setter
    def apispec(self, value):
        self._apispec = value
        self.path = value['path']
        self.path_pattern = pattern_for(value['path'])
        self.operations = {}
        for op in value['operations']:
            self.operations[op['method'].upper()] = self.api.rpc[op['nickname']]

    @classmethod
    def resource_factory(cls, api, apispec):
        meta = cls(api, apispec)
        name = '<{}>'.format(meta.path)
        dct = {'__slots__': ()}
        dct.update(meta.operations)
        resource_class = type(name, (Resource,), dct)
        meta.decorate(resource_class)
        return resource_class


class Resource(object):
    __slots__ = ('_state')


    @classmethod
    def mixin(cls, other):
        cls.__bases__ += (other,)

    def __init__(self, state=None):
        if state is None:
            state = {}
        self._state = state

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(Resource, self).__getattr__(name)
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
                resource = Meta.get(self).api.resources.lookup(key)
                return resource

    def __repr__(self):
        return '{}: {}'.format(self.__class__, self._state)

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
            if 'application/json' in self.opspec.get('consumes', ['application/json']):
                request_args['data'] = json.dumps(jsonify(body))
            else:
                request_args['data'] = body
        res = self.api.connection.request(**request_args)
        if self.type is None:
            return res
        result_state = self.type(_state=res.json())
        if 'meta' in result_state:
            ResultResource = self.api.resources.lookup(
                result_state.meta.href)
            if ResultResource:
                return ResultResource(result_state)
        return result_state

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return self.resource_op_factory(instance)

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

    def resource_op_factory(self, resource):
        '''Bind the path components known in this resource to the path params'''
        mo = Meta.get(resource).path_pattern.search(resource.href)
        bindings = mo.groupdict()
        def call(*args, **kwargs):
            return self.__call__(*args, **dict(bindings, **kwargs))
        return call


class RPCParam(object):

    def __init__(self, pinfo):
        self.name = pinfo['name']
        self.py_name = pinfo['name'].replace('.', '_')
        self.defaultValue = pinfo.get('defaultValue')
        self.paramType = pinfo['paramType']
        func_param_kwargs = {}
        if 'defaultValue' in pinfo:
            func_param_kwargs['default'] = pinfo['defaultValue']
        if 'required' not in pinfo:
            func_param_kwargs['default'] = None
        self.func_param = funcsigs.Parameter(
            self.py_name,
            funcsigs.Parameter.POSITIONAL_OR_KEYWORD,
            **func_param_kwargs)
