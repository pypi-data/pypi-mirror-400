"""Base classes to handle key-value objects in the kvstore"""

from dataclasses import dataclass
import json
import os
import warnings

from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Optional

from conftool import _log, backend as cnf_backend, drivers, types
from conftool.audit import log as audit_log, get_actor
from conftool.configuration import Config


@dataclass
class Field:
    """A specific field within an Entity."""

    name: str
    type: str
    default: Any = None
    docstring: str = ""
    example: str = ""
    hidden: bool = False


class Entity:
    """Basic key-value object implementation."""

    backend: cnf_backend.Backend
    config: Config
    _schema: Dict[str, Any] = {}
    _tags: List
    strict_schema = True
    # Allows to store dependencies
    depends: list = []

    def __init__(self, *tags, wire: Optional[drivers.ObjectWireRepresentation] = None) -> None:
        if len(tags) != (len(self._tags) + 1):
            raise ValueError(
                "Need %s as tags, %s provided" % (",".join(self._tags), ",".join(tags[:-1]))
            )
        self._name = tags[-1]
        self._key = self.kvpath(*tags)
        self._current_tags = {}
        for i, tag in enumerate(self._tags):
            self._current_tags[tag] = tags[i]
        # If data is provided, we initialize from it directly
        # and assume the object exists
        if wire is not None:
            self.from_net(wire.data)
            self.revision_id = wire.metadata.revision_id
            self.exists = True
        else:
            self.fetch()
        self._defaults: Dict[str, Any] = {}

    @classmethod
    def setup(cls, configobj):
        """Set up the client

        This is done by setting the backend and the configuration objects
        that are class properties, so they will be shared among all the
        entities.
        """
        cls.config = configobj
        cls.backend = cnf_backend.Backend(cls.config)

    def kvpath(self, *args):
        return os.path.join(self.base_path(), *args)

    @classmethod
    def query(cls, query):
        """
        Return all matching object given a tag:regexp dictionary as a query

        If any tag (or the object name) are omitted, all of them are supposed to
        get selected.
        """
        tags = cls._tags + ["name"]
        non_existent = set(query.keys()) - set(tags)
        if non_existent:
            raise ValueError(
                "The query includes non-existent tags: {}".format(",".join(non_existent))
            )
        for obj in cls.all():
            is_matching = True
            labels = list(obj.tags.values()) + [obj.name]
            for i, tag in enumerate(tags):
                regex = query.get(tag, None)
                if regex is None:
                    # Label selector not specified, we catch anything
                    continue
                if not regex.match(labels[i]):
                    _log.debug("label %s did not match regex %s", labels[i], regex.pattern)
                    is_matching = False
                    break
            if is_matching:
                yield obj

    @classmethod
    def all(cls) -> List["Entity"]:
        """
        Return all objects of this class
        """
        all_objects = []
        for path, wire in cls.backend.driver.all_objects(cls.base_path()):
            labels = path.replace("//", "/").split("/")
            obj = cls(*labels, wire=wire)
            all_objects.append(obj)
        return all_objects

    @classmethod
    def field_names(cls) -> Iterable[str]:
        return cls._schema.keys()

    def get_field(self, fieldname: str) -> Field:
        s = self._schema.get(fieldname)
        if s is None:
            raise ValueError("Field %s not found in schema" % fieldname)
        return Field(
            fieldname,
            s.expected_type,
            self.get_default(fieldname),
            s.__doc__,
            s.example,
            s.hidden,
        )

    @classmethod
    def base_path(cls):
        raise NotImplementedError("All kvstore objects should implement this")

    @property
    def key(self):
        return self._key

    @property
    def tags(self):
        return self._current_tags

    @classmethod
    def dir(cls, *tags):
        if len(tags) != len(cls._tags):
            raise ValueError("Need %s as tags, %s provided" % (",".join(cls._tags), ",".join(tags)))
        return os.path.join(cls.base_path(), *tags)

    def pprint(self):
        tags_path = os.path.join(*[self._current_tags[tag] for tag in self._tags])
        return os.path.join(tags_path, self._name)

    @property
    def name(self):
        return os.path.basename(self.key)

    def get_default(self, what):
        raise NotImplementedError("All kvstore objects should implement this.")

    def fetch(self):
        self.exists = False
        self.revision_id = -1
        try:
            values = self.backend.driver.read(self.key)
            if values is not None and values.data:
                self.exists = True
                self.revision_id = values.metadata.revision_id
                self.from_net(values.data)
            else:
                self.from_net(None)
        except drivers.NotFoundError:
            self.from_net(None)
        except drivers.BackendError as e:
            _log.error("Backend error while fetching %s: %s", self.key, e)
            # TODO: maybe catch the backend errors separately

    def audit(self, action, success) -> None:
        """Log an audit event"""

        audit_log(
            action=action,
            actor=get_actor(self.backend.driver.actor),
            kind=self.__class__.__name__.lower(),
            obj=self.key,
            success=success,
        )

    def write(self):
        """Write the object to the kvstore"""
        if self.config.read_only:
            _log.info("RO: Would have written %s: %s", self.key, self._to_net())
            return
        try:
            retval = self.backend.driver.write(self.key, self._to_net())
            self.audit("write", True)
            return retval
        except drivers.BackendError:
            self.audit("write", False)
            raise

    def delete(self) -> None:
        """Delete the object from the kvstore"""
        if self.config.read_only:
            _log.info("RO: Would have deleted %s", self.key)
            return
        try:
            self.backend.driver.delete(self.key)
            self.audit("delete", True)
        except drivers.BackendError:
            self.audit("delete", False)
            raise

    @classmethod
    def parse_tags(cls, taglist):
        """Given a taglist as a string, return an ordered list of tags"""

        def tuplestrip(tup):
            return tuple([x.strip() for x in tup])

        tagdict = dict([tuplestrip(el.split("=")) for el in taglist])
        # will raise a KeyError if not all tags are matched
        return [tagdict[t] for t in cls._tags]

    def update(self, values) -> None:
        """
        Update values of properties in the schema
        """
        for k, v in values.items():
            if k not in self._schema:
                continue
            self._set_value(k, self._schema[k], {k: v}, set_defaults=False)
        self.write()

    def changed(self, values: dict) -> Dict:
        """
        Give a set of values, check if it would change the object.

        Arguments:
          values (dict): the values to compare and set

        Returns:
          dict of values that would actually change
        """
        changed = {}
        for k in self._schema:
            current = getattr(self, k)
            if k in values and values[k] != current:
                changed[k] = values[k]
        return changed

    def validate(self, values) -> bool:
        """
        Validate a set of proposed values against the schema.
        Returns None on success, raises an exception otherwise
        """
        for k, v in values.items():
            if k in self._schema:
                validator = self._schema[k]
                validator(v)
            else:
                if self.strict_schema:
                    raise TypeError("Key %s not in the schema" % k)
        return True

    @classmethod
    def from_yaml(cls, data):
        depth = len(cls._tags)
        if depth == 0:
            return {el: None for el in data}
        while depth > 1:
            depth -= 1
            tmpdict = {}
            for k, v in data.items():
                tmpdict.update({("%s/%s" % (k, el)): val for el, val in v.items()})
            data = tmpdict
        tmpdict = {}
        for tags, names in data.items():
            tmpdict.update(dict([("%s/%s" % (tags, name), None) for name in names]))
        return tmpdict

    def from_net(self, values) -> None:
        """
        Fetch the values from the kvstore into the object
        """
        for key, validator in self._schema.items():
            self._set_value(key, validator, values)

    def _to_net(self):
        values = {}
        for key in self._schema:
            try:
                values[key] = getattr(self, key)
            except Exception:
                values[key] = self.get_default(key)
        return values

    def _set_value(self, key, validator, values, set_defaults=True):
        # When initializing a object, we don't really care
        # about logging warnings.
        # Same thing when an object has no value.
        if values is None or values.get(key) is None:
            if set_defaults:
                setattr(self, key, self.get_default(key))
            return

        try:
            setattr(self, key, validator(values[key]))
        except Exception as e:
            _log.info("Value for key %s is invalid: %s", key, e, exc_info=True)
            if set_defaults:
                val = self.get_default(key)
                _log.warning("Setting %s to the default value %s", key, val)
                setattr(self, key, val)
            else:  # pragma: no cover
                _log.warning("Not setting a value")

    def asdict(self):
        d = OrderedDict()
        d[self.name] = self._to_net()
        tags = self.tags
        d["tags"] = ",".join(["%s=%s" % (k, tags[k]) for k in self._tags])
        return d

    def __str__(self):
        return json.dumps(self.asdict())

    def __eq__(self, obj):
        return (
            self.__class__ == obj.__class__
            and self.name == obj.name
            and self.tags == obj.tags
            and self._to_net() == obj._to_net()
        )


class JsonSchemaEntity(Entity):
    """
    Specific class for json-schema based entities
    """

    # loader gets injected into the derived classes when they get generated
    # by loader.factory
    loader = None

    def __init__(self, *tags, wire: Optional[drivers.ObjectWireRepresentation] = None) -> None:
        super().__init__(*tags, wire=wire)
        if self.loader is not None:
            self.rules: List[types.SchemaRule] = self.loader.rules_for(self.tags, self._name)

    def validate(self, values) -> bool:

        # First dump our current value to a json output
        current_values = self._to_net()
        # no additional check is performed, intentionally.
        # This will validate if the final object would respect its schemas
        current_values.update(values)
        for rule in self.rules:
            rule.validate(current_values)
        return True


class FreeSchemaEntity(Entity):
    strict_schema = False

    def __init__(self, *tags, wire: Optional[drivers.ObjectWireRepresentation] = None, **kwargs):
        self._schemaless = kwargs
        super().__init__(*tags, wire=wire)

    def _to_net(self):
        values = super()._to_net()
        for k, v in self._schemaless.items():
            values[k] = v
        return values

    def from_net(self, values) -> None:
        super().from_net(values)
        if values is None:
            return
        for key, value in values.items():
            if key not in self._schema:
                self._schemaless[key] = value

    def changed(self, data: dict) -> bool:  # type: ignore
        """
        Determine if the object would change.

        Given in a free schema entity we'd need a proper diff of keys added
        and removed and that can't be represented as a pure dict,
        we return a boolean instead.
        """
        return self._to_net() != data


# Backawards compatibility aliases


def _backwards_compatibility_warning():
    warnings.warn(
        "KVObject is deprecated, please use Entity instead",
        DeprecationWarning,
        stacklevel=2,
    )


# We define KVObject as a metaclass to allow setters and getters on class
# properties to work as expected
class KVObjectMeta(type):
    @property
    def backend(cls):
        _backwards_compatibility_warning()
        return Entity.backend

    @backend.setter
    def backend(cls, value):
        _backwards_compatibility_warning()
        Entity.backend = value

    @property
    def config(cls):
        _backwards_compatibility_warning()
        return Entity.config

    @config.setter
    def config(cls, value):
        _backwards_compatibility_warning()
        Entity.config = value


class KVObject(metaclass=KVObjectMeta):
    """Alias for Entity for backwards compatibility"""

    @classmethod
    def setup(cls, configobj):
        """Backwards compatibility setup method"""
        warnings.warn(
            "KVObject.setup is deprecated, please use Entity.setup instead",
            DeprecationWarning,
            stacklevel=2,
        )
        Entity.setup(configobj)
