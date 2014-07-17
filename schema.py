"""Simple framework for validating data against a schema.

Schemas are simply dictionaries with expected types in place of
values. All keys in schema are required, and all values of required
keys must be an instance of the required type. Note that instances
of subclasses of the required type are valid.
"""
# TODO: Load Schema from schema descriptor formats?
# TODO: Boolean operators for schemas
# TODO: __instancecheck__ hook
import re
import abc
import collections

class Empty(object):
    pass

EMPTY = Empty()

def dispatch(schema):
    if isinstance(schema, SchemaDescriptor):
        return schema
    elif isinstance(schema, list):
        return List(schema)
    elif isinstance(schema, dict):
        return Map(schema)
    #elif isinstance(schema, set):
    #    return Set(schema)
    elif isinstance(schema, type):
        return Instance(schema)
    else:
        raise TypeError("{} not a valid schema descriptor.".format(schema))

class SchemaDescriptor(object):
    __metaclass__ = abc.ABCMeta
    typ = None

    def __init__(self, schema):
        if not isinstance(schema, self.typ):
            raise TypeError("Schema {} must be type {}.".format(schema, self.typ))

        self.schema = schema

    @abc.abstractmethod
    def coerce(self, data):
        """Validates the data according to the descriptor's rules.

        If valid, return the data (plus any transformations necessary).
        If not valid, throw TypeError.
        """
        pass

    def validate(self, data):
        try:
            self.coerce(data)
        except ValueError:
            return False
        else:
            return True


class RegEx(SchemaDescriptor):
    def __init__(self, pattern, flags=0):
        self.pattern = pattern
        self.flags = flags

    def coerce(self, data):
        try:
            result = re.search(self.pattern, data, flags=self.flags)
        except (TypeError, ValueError):
            raise ValueError

        if result:
            return data
        else:
            raise ValueError

class Email(RegEx):
    def __init__(self):
        self.pattern = '^[-0-9a-zA-Z.+_]+@[-0-9a-zA-Z.+_]+\.[a-zA-Z]+$'
        self.flags = 0

##############
# BASE CASES #
##############

class Instance(SchemaDescriptor):
    typ = type
    def coerce(self, data):
        if isinstance(data, self.schema):
            return data
        else:
            raise ValueError

class Coerce(SchemaDescriptor):
    def __init__(self, schema):
        if not callable(schema):
            raise TypeError('Arguments to Coerce must be callable.')
        self.schema = schema

    def coerce(self, data):
        return self.schema(data)

class Check(SchemaDescriptor):
    def __init__(self, schema):
        if not callable(schema):
            raise TypeError('Arguments to Check must be callable.')
        self.schema = schema

    def coerce(self, data):
        if self.schema(data):
            return data

        raise ValueError

###############
# COLLECTIONS #
###############

class List(SchemaDescriptor):
    typ = list
    def __init__(self, schema):
        if not isinstance(schema, list):
            raise TypeError('List only takes lists as schema. {} is not a list.'.format(schema))

        if len(schema) != 1:
            raise TypeError('Only homogenous containers allowed.')

        self.schema = dispatch(schema[0])

    def coerce(self, data):
        if not isinstance(data, list):
            raise ValueError

        # TODO: schema_type property?
        new = []
        for item in data:
            new.append(self.schema.coerce(item))

        return new

class Map(SchemaDescriptor):
    def __init__(self, schema):
        if not isinstance(schema, collections.MutableMapping):
            raise TypeError("Map may only take mappings as schema. {} is not a mapping.".format(schema))

        self.schema = schema

    def coerce(self, data):
        if not isinstance(data, collections.MutableMapping):
            raise ValueError

        new = {}
        keys = set(data.keys())
        for key, schema in self.schema.iteritems():
            val = data.get(key, EMPTY)
            schema = dispatch(schema)
            new[key] = schema.coerce(val)
            keys.remove(key)

        if keys:
            raise ValueError

        return new

#############
# OPTIONALS #
#############

class Optional(SchemaDescriptor):
    def __init__(self, schema, default=None):
        if default and not isinstance(default, schema):
            raise ValueError("Default {} must validate against type {}.".format(default, schema))

        self.schema = dispatch(schema)
        self.default = default

    def coerce(self, data):
        if data is EMPTY:
            return self.default
        else:
            return self.schema.coerce(data)

class OptionalString(Optional):
    def __init__(self, default):
        if default and not isinstance(default, basestring):
            raise ValueError("OptionalString requires a default string. {} is not a string.".format(default))

        self.schema = dispatch(str)
        self.default = default

    def coerce(self, data):
        if data == '' or data is EMPTY:
            return self.default
        else:
            return self.schema.coerce(data)

