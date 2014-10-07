from .decorator import reify

class Unset(object):
    pass
Unset = Unset()

class Model(object):
    __slots__ = ('_state',)

    def __init__(self, **kwargs):
        self._state = kwargs.pop('_state', self.__meta__['default_state'])
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def class_factory(cls, api, model_or_id):
        if isinstance(model_or_id, basestring):
            js_model = api.spec.model(model_or_id)
        else:
            js_model = model_or_id
        required = set(js_model.get('required', []))
        properties = {}
        default_state = {}
        dct = {
            '__slots__': (),
            '__meta__': dict(
                api=api,
                required=required,
                properties=properties,
                js_model=js_model,
                default_state=default_state)}
        for pname, pdata in js_model['properties'].items():
            prop = Property.factory(api, pdata)
            dct[pname] = prop
            properties[pname] = prop
            if prop.defaultValue is not Unset:
                default_state = prop.defaultValue
        cls = type(js_model['id'].encode('utf-8'), (cls,), dct)
        for pname, prop in properties.items():
            prop.bind_name(pname)
        return cls

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self._state))

    def __json__(self):
        return self._state

    def __contains__(self, key):
        return key in self._state

    def __getattr__(self, name):
        try:
            return self._state[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == '_state':
            super(Model, self).__setattr__(name, value)
        elif self.__meta__['js_model'].get('additionalProperties'):
            self._state[name] = value
        else:
            super(Model, self).__setattr__(name, value)


class Property(object):
    _registry = {}
    defaultValue = Unset

    def __init__(self, api, **kwargs):
        self._api = api
        self._pinfo = kwargs
        self._name = None
        if 'defaultValue' in kwargs:
            setattr(self, 'defaultValue', kwargs['defaultValue'])

    def bind_name(self, attr_name):
        self._attr_name = attr_name

    def __repr__(self):
        parts = [self.__class__.__name__]
        if self._attr_name:
            parts.append(self._attr_name)
        return '<{}>'.format(' '.join(parts))

    @classmethod
    def factory(cls, api, pdata):
        if '$ref' in pdata:
            return ModelProperty(api, **pdata)
        ptype = pdata['type']
        subcls = cls._registry[ptype]
        inst = subcls(api, **pdata)
        return inst

    @classmethod
    def register(cls, type_spec):
        def decorator(subcls):
            cls._registry[type_spec] = subcls
        return decorator

    def marshal(self, value):
        '''Convert value into something json-safe'''
        return value

    def unmarshal(self, value):
        '''Convert value from something json-safe'''
        return value

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return self.unmarshal(instance._state[self._attr_name])

    def __set__(self, instance, value):
        instance._state[self._attr_name] = self.marshal(value)

    def __delete__(self, instance):
        del instance._state[self._attr_name]


class ModelProperty(Property):

    @reify
    def _model_id(self):
        return self._pinfo['$ref']

    def marshal(self, value):
        return value._state

    def unmarshal(self, value):
        Model = self._api.models[self._model_id]
        return Model(_state=value)

@Property.register('array')
class ArrayProperty(Property):

    @reify
    def _items(self):
        return self._pinfo['items']

    @reify
    def _item_property(self):
        return Property.factory(self._api, self._items)

    def marshal(self, values):
        return [self._item_property.marshal(v) for v in values]

    def unmarshal(self, values):
        return [self._item_property.unmarshal(v) for v in values]


@Property.register('string')
class StringProperty(Property):
    pass

@Property.register('integer')
class IntegerProperty(Property):
    pass

@Property.register('number')
class NumberProperty(Property):
    pass

@Property.register('boolean')
class BooleanProperty(Property):
    pass

