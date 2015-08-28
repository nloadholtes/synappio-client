'''Super-simple Pyramid App for converting .yml files to .json'''
import json
import os.path
import logging

import yaml
import jinja2
import pkg_resources
from pyramid.config import Configurator
import pyramid.httpexceptions as exc


log = logging.getLogger(__name__)


class DocServer(object):

    def __init__(self, egg, resource_name):
        self.loader = DocLoader(egg, resource_name)

    @classmethod
    def factory(cls, global_config, egg, resource_name):
        self = DocServer(egg, resource_name)
        config = Configurator(settings=global_config)
        config.add_route('catchall', '/*subpath')
        config.add_view(self.view, route_name='catchall', renderer='json')
        app = config.make_wsgi_app()
        return app

    def view(self, request):
        subpath = request.matchdict['subpath']
        fn = '/'.join(subpath)
        norm_fn = self.loader.normalize_filename(fn)
        if os.path.isdir(norm_fn):
            norm_fn += '/swagger.json'
        return self.loader.load_filename(norm_fn)

    def load_yaml(self, source_fn):
        with open(source_fn) as fp:
            return yaml.load(fp)

    def load_yaml_jinja(self, source_fn):
        rel_fn = os.path.relpath(source_fn, self.root_resource_path)
        template = self.jinja_env.get_template(rel_fn)
        yaml_text = template.render()
        try:
            return yaml.load(yaml_text)
        except yaml.parser.ParserError as err:
            problem_line = err.problem_mark.line
            buffer_lines = err.problem_mark.buffer.splitlines()
            min_line, max_line = max(1, problem_line - 10), min(problem_line + 10, len(buffer_lines)+1)
            for line_no0 in range(min_line-1, max_line):
                if line_no0 == problem_line - 1:
                    sep = ' * '
                else:
                    sep = '   '
                print '{:05d} {} {}'.format(line_no0 + 1, sep, buffer_lines[line_no0])
            raise


class DocLoader(object):

    def __init__(self, egg, resource_name):
        self.manager = pkg_resources.ResourceManager()
        self.egg = pkg_resources.get_distribution(egg)
        self.resource_name = resource_name
        self.root_resource_path = self.egg.get_resource_filename(
            self.manager, resource_name)
        self.search_path = [self.root_resource_path]
        self.jinja_loader = jinja2.FileSystemLoader(self.search_path)
        self.jinja_env = jinja2.Environment(loader=self.jinja_loader)

    def normalize_filename(self, fn):
        result = os.path.normpath(os.path.join(self.root_resource_path, fn))
        if result.startswith(self.root_resource_path):
            return result
        else:
            log.error('Could not load filename %s in any of %s', result, self.search_path)
            raise exc.HTTPNotFound()

    def load_filename(self, fn):
        try:
            base, ext = os.path.splitext(fn)
            exts = [ext]
            if ext == '.json':
                exts += ['.json.jinja', '.yaml.jinja', '.yaml']
            for ext in exts:
                full_fn = base + ext
                if not os.path.exists(full_fn):
                    continue
                if ext == '.json.jinja':
                    content_json = self.render_jinja(full_fn)
                    data = json.loads(content_json)
                    return data
                elif ext == '.yaml.jinja':
                    content_yaml = self.render_jinja(full_fn)
                    data = yaml.load(content_yaml)
                    return data
                with open(full_fn) as fp:
                    if ext == '.yaml':
                        return yaml.load(fp)
                    elif ext == '.json':
                        return json.load(fp)
            raise exc.HTTPNotFound()
        except Exception:
            log.error('Could not load filename %s in any of %s', fn, self.search_path)
            raise

    def render_jinja(self, fn):
        rel_fn = os.path.relpath(fn, self.root_resource_path)
        template = self.jinja_env.get_template(rel_fn)
        return template.render()
