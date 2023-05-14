# coding: utf-8
from __future__ import unicode_literals


__documented_introspection_query = """
query IntrospectionQuery {
    __schema {
        # Typically query is called "Query" and mutation "Mutation", but those can be redefined.
        # For some reason, spec does not force queryType[name] to be String!, but I don't think it can be null.
        queryType {
            name
        }
        # 'mutationType' can be null if there are no mutations.
        mutationType {
            name
        }
        # TODO: We're not parsing subscriptions and directives at all right now
        # subscriptionType { name }
        # directives { name }
        types {
            name
            # 'kind' is enum with values: SCALAR, OBJECT, INTERFACE, UNION, ENUM, INPUT_OBJECT, LIST, NON_NULL
            kind
            description
            # The following are only present for OBJECT and INTERFACE, otherwise null:
            fields(includeDeprecated: true) {
                name
                description
                args%(args_includeDeprecated)s {
                    ... InputValue
                }
                type {
                    ... TypeRef
                }
                isDeprecated
                deprecationReason
            }
            interfaces {
                ... TypeRef
            }
            # The following is only non-null for INTERFACE and UNION:
            possibleTypes {
                ... TypeRef
            }
            # The following is only non-null for ENUM:
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            # The following is only non-null for INPUT_OBJECT:
            inputFields%(inputFields_includeDeprecated)s {
                ... InputValue
            }
            # The following is only non-null for LIST and NON_NULL:
            ofType {
                ... TypeRef
            }
            # Only (optionally) non-null for custom scalars:
            %(specifiedByURL)s
        }
    }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

# TODO: generate this query dynamically and make the depth adjustable
fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
"""


# TODO: 'depth' is ignored right now, fix it
def get_introspection_query(version='draft', depth=4, minimize=True):
    """Construct the introspection query and optionally minimize it."""
    if version == 'draft':
        # https://spec.graphql.org/draft/
        # Args and inputFields have includeDeprecated selector
        query = __documented_introspection_query % {
            'args_includeDeprecated': '(includeDeprecated: true) ',
            'inputFields_includeDeprecated': '(includeDeprecated: true)',
            'specifiedByURL': 'specifiedByURL'
        }
    elif version == 'oct2021':
        # https://spec.graphql.org/October2021/
        # Args and inputFields can't have includeDeprecated, but specifiedByURL exists
        query = __documented_introspection_query % {
            'args_includeDeprecated': '',
            'inputFields_includeDeprecated': '',
            'specifiedByURL': 'specifiedByURL'
        }
    elif version == 'jun2018':
        # https://spec.graphql.org/June2018/
        # No includeDeprecated and no specifiedByURL either
        query = __documented_introspection_query % {
            'args_includeDeprecated': '',
            'inputFields_includeDeprecated': '',
            'specifiedByURL': ''
        }
    else:
        raise Exception("Version '%s' is invalid." % version)

    return query
