import json

import yaml
import requests
import jsonschema as S

import formencode as fe
from formencode import validators as fev


class SwaggerSpec(object):

    def __init__(self, path=None):
        self.resolver = None
        if path is not None:
            self.load(path)

    def load(self, path):
        # Load content
        if '://' in path:
            content = requests.get(path).text
        else:
            with open(path) as fp:
                content = fp.read()
        # Deserialize
        if path.endswith('.json'):
            self._raw = json.loads(content)
        elif path.endswith('.yaml'):
            self._raw = yaml.load(content)
        # Build resolver
        self.resolver = S.RefResolver(path, self._raw)
        self._index_operations()
        self.basePath = self._raw['basePath']

    def iter_models(self):
        for id in self._raw['models']:
            yield self.model(id)

    def iter_apis(self):
        for api in self._raw['apis']:
            yield api

    def model(self, id):
        model = self._raw['models'][id]
        if model['id'] != id:
            raise fev.Invalid('id mismatch: {} != {}'.format(id, model['id']),
                model, None)
        model.setdefault('type', 'object')
        model.setdefault('additionalProperties', False)
        return model

    def params(self, path, method, paramType):
        operation = self.get_operation(path, method)
        # Build a JSON schema out of our matching parameters
        properties = {}
        required = []
        for p in operation['parameters']:
            if p['paramType'] != paramType:
                continue
            properties[p['name']] = {'type': p['type']}
            if p.get('required'):
                required.append(p['name'])
        if paramType == 'body':
            if properties.keys() != ['body']:
                raise fe.Invalid(
                    'paramType="body" requires one property with the name "body"',
                    operation['parameters'], None)
            return self.model(properties['body']['type'])
        model = {
            'type': 'object',
            'properties': properties,
            'additionalProperties': False}
        if required:
            model['required'] = required
        return model

    def output(self, path, method):
        op = self.get_operation(path, method)
        if 'type' in op:
            return self.model(op['type'])

    def get_api(self, path):
        try:
            return self._operation_index[path]
        except KeyError:
            raise fe.Invalid(
                'Unknown path: {}'.format( path),
                self._raw, None)

    def get_operation(self, path, method):
        try:
            return self._operation_index[path][method.upper()]
        except KeyError:
            raise fe.Invalid(
                'Unknown operation: {} {}'.format(method, path),
                self._raw, None)

    def _index_operations(self):
        self._operation_index = {}
        for api in self._raw['apis']:
            self._operation_index[api['path']] = ops = {}
            for op in api['operations']:
                ops[op['method'].upper()] = op


