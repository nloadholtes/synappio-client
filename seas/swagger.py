import re
import os
import logging
import urlparse

import jsonschema as S

import formencode as fe
from formencode import validators as fev

from seas import doc
from seas.util import pattern_for, extend_dict


log = logging.getLogger(__name__)
re_path_loader = re.compile(r'^(.*)\[(.*)\]$')


class SwaggerSpec(object):

    def __init__(self, path=None):
        self.resolver = None
        self._operation_index = {}
        self._path_patterns = None
        if path is not None:
            self.load(path)

    def load(self, path):
        self._raw = {}
        parsed = urlparse.urlparse(path)
        mo = re_path_loader.match(parsed.path)
        if mo:
            loader = doc.DocLoader(parsed.netloc, mo.group(1))
            fn = loader.normalize_filename(mo.group(2))
        else:
            loader = doc.DocLoader(parsed.netloc, os.path.dirname(parsed.path))
            fn = loader.normalize_filename(os.path.basename(parsed.path))
        to_load = [fn]
        while to_load:
            p = to_load.pop(0)
            fn = loader.normalize_filename(p)
            try:
                content_data = loader.load_filename(fn)
            except Exception as err:
                log.error('Error loading resource at %s: %s', fn, err)
                raise
            if 'resourcePath' in content_data:
                extend_dict(self._raw, content_data)
            else:
                # Must be a swagger.yaml file
                for api in content_data['apis']:
                    new_path = api['path']
                    if new_path.startswith('/'):
                        new_path = '.' + new_path
                    new_path = os.path.join(os.path.dirname(fn), new_path)
                    new_path = os.path.normpath(new_path)
                    to_load.append(new_path)
        # Build resolver
        self.resolver = ModelRefResolver(path, self._raw)
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
        if 'id' not in model:
            raise fev.Invalid(
                'No id field for model {}'.format(id),
                model, None)
        if model['id'] != id:
            raise fev.Invalid(
                'id mismatch: {} != {}'.format(id, model['id']),
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
            properties[p['name']] = dict(p) # {'type': p['type']}
            if p.get('required'):
                required.append(p['name'])
        if paramType == 'body':
            if not properties:
                return None
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
        if paramType in ('header', 'query'):
            model['additionalProperties'] = True
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
        self._path_patterns = []
        for i, api in enumerate(self._raw['apis']):
            path = api['path']
            self._path_patterns.append(
                (pattern_for(api['path']), api['path']))
            self._operation_index[path] = ops = {}
            for op in api['operations']:
                ops[op['method'].upper()] = op

    def swagger_path_by_request_path(self, request_path):
        matches = []
        for regex, path in self._path_patterns:
            if regex.search(request_path):
                matches.append(path)
        if not matches:
            return None
        matches.sort(key=len)
        return matches[-1]


class ModelRefResolver(S.RefResolver):

    def resolving(self, ref):
        self.resolution_scope = self.base_uri
        new_ref = '#/models/' + ref
        return super(ModelRefResolver, self).resolving(new_ref)

