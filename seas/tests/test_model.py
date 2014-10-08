import unittest

from seas import api, model

class TestModel(unittest.TestCase):
    swagger = {
        'Point': {
            'id': 'Point',
            'properties': {
                'x': {'type': 'integer', 'defaultValue': 0},
                'y': {'type': 'integer', 'defaultValue': 0}
            }
        }
    }

    def setUp(self):
        self.api = api.API('egg://synappio-client/seas/tests/empty.yaml')

    def test_model_with_defaults(self):
        Point = model.ModelMeta.model_factory(self.api, self.swagger['Point'])
        print Point()
