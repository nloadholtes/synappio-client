from copy import deepcopy

from .decorator import reify

class Unset(object):
    def __repr__(self):
        return '-UNSET-'
Unset = Unset()

class Meta(object):
    attr_name = '__meta__'

    def __init__(self, api):
        self.api = api

    @classmethod
    def get(cls, other):
        return getattr(other, cls.attr_name)

    def decorate(self, other):
        setattr(other, self.attr_name, self)


class ModelMeta(Meta):
    state_attr_name = '__model_state__'

    def __init__(self, api, model_or_id):
        super(ModelMeta, self).__init__(api)
        self._js_model = Unset
        self.id = Unset
        self.required = Unset
        self.properties = Unset
        self.additionalProperties = Unset
        self.default_state = Unset

        if isinstance(model_or_id, basestring):
            self.js_model = api.spec.model(model_or_id)
        else:
            self.js_model = model_or_id

    @property
    def js_model(self):
        return self._js_model
    @js_model.setter
    def js_model(self, js_model):
        self._js_model = js_model
        self.id = js_model['id'].encode('utf-8')
        self.additionalProperties = js_model.get('additionalProperties', False)
        self.required = set(js_model.get('required', []))
        self.properties = {}
        self.default_state = {}
        for pname, pdata in js_model['properties'].items():
            prop = Property.factory(self.api, pdata, pname)
            self.properties[pname] = prop
            prop_meta = Meta.get(prop)
            if prop_meta.defaultValue is not Unset:
                self.default_state[pname] = prop_meta.defaultValue

    @classmethod
    def model_factory(cls, api, model_or_id):
        meta = cls(api, model_or_id)
        dct = {'__slots__': (), cls.attr_name: meta}
        dct.update(meta.properties)
        model_cls = type(meta.id, (Model,), dct)
        meta.decorate(model_cls)
        return model_cls

    def get_state(self, inst):
        return getattr(inst, self.state_attr_name)

    def set_state(self, inst, value):
        if value is Unset:
            value = deepcopy(self.default_state)
        setattr(inst, self.state_attr_name, value)

    def get_state_item(self, inst, name):
        return self.get_state(inst)[name]

    def set_state_item(self, inst, name, value):
        self.get_state(inst)[name] = value

    def del_state_item(self, inst, name):
        del self.get_state(inst)[name]


class PropertyMeta(Meta):
    _registry = {}

    def __init__(self, api, pinfo, name=Unset):
        super(PropertyMeta, self).__init__(api)
        self._pinfo = Unset
        self.defaultValue = Unset
        self.name = name
        self.pinfo = pinfo

    @property
    def pinfo(self):
        return self._pinfo
    @pinfo.setter
    def pinfo(self, pinfo):
        self._pinfo = pinfo
        self.defaultValue = pinfo.get('defaultValue', Unset)


class Model(object):
    __slots__ = (ModelMeta.state_attr_name,)

    def __init__(self, **kwargs):
        meta = Meta.get(self)
        meta.set_state(self, kwargs.pop('_state', Unset))
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            Meta.get(self).get_state(self))

    def __json__(self):
        meta = Meta.get(self)
        return meta.get_state(self)

    def __contains__(self, key):
        meta = Meta.get(self)
        return key in meta.get_state(self)

    def __getattr__(self, name):
        meta = Meta.get(self)
        try:
            return meta.get_state_item(self, name)
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super(Model, self).__setattr__(name, value)
        try:
            return super(Model, self).__setattr__(name, value)
        except AttributeError:
            meta = Meta.get(self)
            if meta.additionalProperties:
                meta.set_state_item(self, name, value)
            else:
                raise


class Property(object):
    _registry = {}

    def __init__(self, api, pinfo, name=Unset):
        meta = PropertyMeta(api, pinfo, name)
        meta.decorate(self)

    def __repr__(self):
        meta = Meta.get(self)
        parts = [self.__class__.__name__, meta.name]
        return '<{}>'.format(' '.join(parts))

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(Property, self).__getattr__(name)
        return getattr(Meta.get(self), name)

    @classmethod
    def factory(cls, api, pinfo, pname=Unset):
        if '$ref' in pinfo:
            return ModelProperty(api, pinfo, pname)
        ptype = pinfo['type']
        subcls = cls._registry[ptype]
        inst = subcls(api, pinfo, pname)
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
        my_meta = Meta.get(self)
        inst_meta = Meta.get(instance)
        value = inst_meta.get_state_item(instance, my_meta.name)
        return self.unmarshal(value)

    def __set__(self, instance, value):
        value = self.marshal(value)
        my_meta = Meta.get(self)
        inst_meta = Meta.get(instance)
        inst_meta.set_state_item(instance, my_meta.name, value)

    def __delete__(self, instance):
        my_meta = Meta.get(self)
        inst_meta = Meta.get(instance)
        inst_meta.del_state_item(instance, my_meta.name)


class ModelProperty(Property):

    @reify
    def _model_id(self):
        return Meta.get(self).pinfo['$ref']

    def marshal(self, value):
        return Meta.get(value).get_state(value)

    def unmarshal(self, value):
        Model = Meta.get(self).api.models[self._model_id]
        return Model(_state=value)


@Property.register('array')
class ArrayProperty(Property):

    @reify
    def item_property(self):
        meta = Meta.get(self)
        return Property.factory(meta.api, meta.pinfo['items'])

    def marshal(self, values):
        return [self.item_property.marshal(v) for v in values]

    def unmarshal(self, values):
        return [self.item_property.unmarshal(v) for v in values]


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

