# coding: utf-8
from __future__ import unicode_literals

from gqlspection.six import ensure_text


class GQLTypeKind(object):
    """Construct a type out of GraphQL schema fragment.

    Type kinds are stored in the 'kind' property, which is defined by __TypeKind enum:

        enum __TypeKind {
          SCALAR
          OBJECT
          INTERFACE
          UNION
          ENUM
          INPUT_OBJECT
          LIST             # wrapping type, need to check 'ofType' to construct the whole type
          NON_NULL         # wrapping type, need to check 'ofType' to construct the whole type
        }

    Additionally, note that the introspection_query we use only queries first level data, the nested types only return
    name and kind. That is, in order to query fields, interfaces, possibleTypes, enumValues, inputFields, inputFields,
    ofType and specifiedByURL you need to use the first-level definition within the schema[].

    A typedef is schema fragment such as:

        {u'kind': u'NON_NULL',
         u'name': None,
         u'ofType': {u'kind': u'LIST',
          u'name': None,
          u'ofType': {u'kind': u'NON_NULL',
           u'name': None,
           u'ofType': {u'kind': u'OBJECT',
            u'name': u'BillingPlanV2',
            u'ofType': None}}}}

    """
    wrapping_types = ('LIST', 'NON_NULL')
    non_wrapping_types = ('SCALAR', 'OBJECT', 'INTERFACE', 'UNION', 'ENUM', 'INPUT_OBJECT')
    leaf_types = ('SCALAR', 'ENUM')
    builtin_scalars = ('Int', 'Float', 'String', 'Boolean', 'ID')

    # in the example above: [NON_NULL, LIST, NON_NULL]
    modifiers = None
    # in the example above: OBJECT
    kind = None
    # in the example above: 'BillingPlanV2'
    name = None

    def __init__(self, name, kind, modifiers=None):
        # type: (str, GQLTypeKind, Optional[list[str]]) -> None
        self.name = ensure_text(name)
        self.kind = kind
        self.modifiers = modifiers or []
        self._is_builtin_scalar = None
        self._is_leaf = None
        self._is_final = None
        self.isbs = None
        self.isl = None
        self.isf = None

    @staticmethod
    def from_json(typedef):
        current = typedef
        modifiers = []
        while current['kind'] in GQLTypeKind.wrapping_types:
            # iterate through intermediate modifiers (LIST and NON_NULL)
            modifiers.append(current['kind'])
            current = current['ofType']

        # by this time all modifiers should have been parsed, make sure the result is what we expect
        if current['kind'] not in GQLTypeKind.non_wrapping_types:
            raise Exception("GQLTypeKind: Type '%s' is of unknown kind: '%s'" % (typedef['name'], typedef['kind']))

        return GQLTypeKind(
            name=current['name'],
            kind=current['kind'],
            modifiers=modifiers
        )

    # String representation (in the example above: "[BillingPlanV2!]!")
    def __repr__(self):
        string_representation = self.name
        for modifier in reversed(self.modifiers):
            if modifier == 'NON_NULL':
                string_representation += '!'
            if modifier == 'LIST':
                string_representation = "[%s]" % string_representation

        return string_representation

    @property
    def is_builtin_scalar(self):
        value = self._is_builtin_scalar
        if value is not None:
            return value

        value = self.name in self.builtin_scalars
        self._is_builtin_scalar = value
        return value

    @property
    def is_leaf(self):
        value = self._is_leaf
        if value is not None:
            return value

        value = self.kind in self.leaf_types
        self._is_leaf = value
        return value

    @property
    def is_final(self):
        value = self._is_final
        if value is not None:
            return value

        value = self.is_leaf or self.is_builtin_scalar
        self._is_final = value
        return value
