import json
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
        self.models = dict(
            (model['id'], Model.factory(self, model))
            for model in self.spec.iter_models())
        self.rpc = RPCOperations(self)

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

class Models(object):

    def __init__(self, api):
        self._models = dict(
            (model['id'], Model.factory(self, model))
            for model in self.spec.iter_models())

    def __getattr__(self, name):
        try:
            return self._models[name]
        except:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._models[name]



class RPCOperations(object):

    def __init__(self, api):
        self._operations = dict(
            (opspec['nickname'], RPCOp(api, apispec['path'], opspec))
            for apispec in api.spec.iter_apis()
            for opspec in apispec['operations'])

    def __getattr__(self, name):
        try:
            return self._operations[name]
        except:
            raise AttributeError(name)

    def __getitem__(self, name):
        return self._operations[name]



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
        return self.type(_state=res.json())

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
