# coding: utf-8
# These functions are generated by ChatGPT (https://chat.openai.com/chat), Dec 15 [2022] Version.
# According to ChatGPT, the code is licensed under MIT license.

from __future__ import unicode_literals
from gqlspection import log
from gqlspection.six import text_type
from gqlspection.introspection_query import get_introspection_query


def minimize_query(query):
    # Set up a buffer for the minimized query
    minimized = ""

    # Set up a flag to track whether we are inside a comment
    in_comment = False

    # Set up a flag to track whether we are inside a string
    in_single_string = False
    in_double_string = False
    in_string = False

    # Set up a flag to track whether we are inside a whitespace
    in_space = False

    # Set up a flag to track whether the current character is an escaped quote
    escaped = False

    # Iterate over each character in the query
    for c in query.strip():
        # If we see the start of a comment and we are not inside a string,
        # set the in_comment flag
        if c == "#" and not in_string:
            in_comment = True

        # Preserve strings verbatim
        if in_string:
            minimized += c
        # Skip comments entirely
        elif not in_comment:
            # Collapse all whitespace into one space character
            if in_space:
                if not c.isspace():
                    minimized += " " + c
            elif not c.isspace():
                minimized += c

        # If we are inside a whitespace, set the in_space flag
        in_space = c.isspace()

        # If we see the end of a comment and we are not inside a string,
        # clear the in_comment flag
        if not in_string and (c == "\n"):
            in_comment = False

        # Toggle the in_*_string flags if we see quote character, unless it's escaped
        if not in_comment and not escaped:
            in_double_string = not in_double_string if c == '"' else in_double_string
            in_single_string = not in_single_string if c == "'" else in_single_string
        in_string = in_single_string or in_double_string

        # Set the escaped flag, if the current character is a backslash
        escaped = (c == "\\")

    # Return the minimized query
    return minimized


# The opposite of the above, note that there can't be any comments in a minimized GraphQL query
def pretty_print_graphql(minimized, spaces=2):
    pretty = ""

    level = 0

    in_single_string = False
    in_double_string = False
    in_string = False
    in_space = False
    parenthesis = False
    nuke_space = False
    brace = False

    escaped = False
    keep_spaces = False

    for c in minimized.strip():
        #
        # 1. Special case 'nuke space' used after newlines
        #
        if nuke_space:
            # Skip all of the whitespace until first non-whitespace char
            if c.isspace():
                continue
            in_space, nuke_space = False, False

        #
        # 2. Deal with strings - ignore all other rules, even whitespace until string is over
        #
        was_in_string = in_string
        if not escaped:
            in_double_string = not in_double_string if c == '"' else in_double_string
            in_single_string = not in_single_string if c == "'" else in_single_string
        in_string = in_single_string or in_double_string
        if was_in_string:
            # Preserve strings verbatim, just check whether current char is backslash
            pretty += c
            escaped = (c == "\\")
            continue

        #
        # 3. A few elements that care about spaces on the left of them, so should be parsed before 4.
        #

        # Space around =
        if c == '=':
            # Add space on left, ignoring other stuff there
            pretty += ' ='
            # space on the right will get added on next iteration, but if there was preexisting
            # whitespace all of it will get collapsed into a single char
            in_space = True
            continue

        # Make sure there's space on the left of {
        if c == '{':
            level += 1
            if not len(pretty):
                # ... unless it is the simple GraphQL query that starts with { right away (no name and not even 'query')
                pretty += '{\n' + ' ' * spaces
            else:
                pretty += ' ' + '{\n' + ' ' * (level * spaces)
            keep_spaces = False
            nuke_space, in_space = True, False
            continue

        #
        # 4. Normally all whitespace gets collapsed into a single space char
        #
        if c.isspace():
            # Mark a string of whitespace
            in_space = True
            continue
        if in_space:
            # The string of whitespace is over, add a single space char or a whole new newline.
            # An heuristic for now: we should always add a newline when there's space, unless:
            #
            #   1. we see ':' before the space (alias)
            #   2. we see '(' before the space (various arguments)
            #   3. we see '@' as  first char *after* the space
            #   4. we are at the outmost context (no {} around us)
            #
            # In 1-3 we should keep spaces until first '{' and then add newlines
            # In 4 we should just do nothing as newline will be added elsewhere

            if (keep_spaces or
                    (pretty[-1] in (':', '(')) or
                    (not level) or
                    (c == '@')):
                # match one of the heuristics above, keep spaces until first '{'
                keep_spaces = True
                pretty += ' '
            elif c != '}':
                pretty += '\n' + ' ' * (level * spaces)
        # Mark the end of whitespace string
        in_space = False

        #
        # 5. The rest shouldn't care whether there were spaces before or not
        #

        # Space after : and )
        if c in (':', ')'):
            pretty += c
            in_space = True
            continue

        # Put } on a new line
        if c == '}':
            brace = True
            level -= 1
            pretty += '\n' + ' ' * (level * spaces) + '}'
            nuke_space = True
            continue
        if brace:
            if not level:
                # Multiple queries (or more likely fragments) should be separated by whitespace
                pretty += '\n'
            # Next element on the same level as previous closed brace
            pretty += '\n' + ' ' * (level * spaces)
            brace = False

        # Add space after the last parenthesis
        if c == ')':
            parenthesis = True
            continue
        if parenthesis:
            pretty += ' '
        parenthesis = False

        # If reached this, the current character is something boring, just add it and be done
        pretty += c

    return pretty


def format_comment(string, max_length=60):
    """Format a comment to be no longer than max_length characters per line."""

    # Split the string into lines
    lines = string.split('\n')

    # Initialize a list to store the formatted lines
    formatted_lines = []

    # Iterate through the lines
    for line in lines:
        # Split the line into words
        words = line.split()

        # Initialize a variable to keep track of the current line
        current_line = ''

        # Iterate through the words
        for word in words:
            # If the current line plus the next word would be too long,
            # append the current line to the list of formatted lines and start a new line
            if len(current_line) + len(word) > max_length:
                formatted_lines.append(current_line)
                current_line = ''

            # If the current line is empty, add the word to the line
            # Otherwise, add a space and the word to the line
            if current_line == '':
                current_line = word
            else:
                current_line += ' ' + word

        # Add the remaining line to the list of formatted lines
        formatted_lines.append(current_line)

    # Return the formatted comment
    return '\n'.join(['# ' + line for line in formatted_lines])


def safe_get_list(dictionary, name):
    """Safely extract list from the dictionary, even if the key does not exist or type is wrong."""
    res = dictionary.get(name, [])

    if type(res) is list:
        return res
    else:
        return []


def pad_string(string, n=4):
    """Pad a multiline string with n spaces."""
    if not n or not string:
        return string

    if type(string) == text_type:
        ends_with_newline = string[-1] == '\n'
        return '\n'.join((
            (' ' * n + line) for line in string.splitlines()
        )) + ('\n' if ends_with_newline else '')
    else:
        log.debug("Asked to pad the following non-string with %s spaces: %s", n, string)
        raise Exception("Expected a string to pad, received %s", type(string))


def query_introspection_version(url, headers=None, version='draft', include_metadata=False, request_fn=None):
    """
    Send introspection query with the specified version and get the GraphQL schema.
    """
    log.debug("Introspection query about to be sent with version '%s' to '%s'.", version, url)

    # Get the introspection query
    body = '{{"query":"{}"}}'.format(get_introspection_query(version=version))
    log.debug("Acquired introspection query body")

    # Use requests library by default, but allow overriding
    if not request_fn:
        from requests import request as request_fn

    # Use application/json by default, but allow overriding
    if not headers:
        headers = {'Content-Type': 'application/json'}

    # Send HTTP request
    response = request_fn('POST', url, headers=headers, data=body)
    log.debug("Sent the request and got the response")

    try:
        schema = response.json()
        log.debug("successfully parsed JSON")
    except Exception:
        # TODO: Doesn't this mean it's not a GraphQL endpoint? Maybe early return?
        log.info("Could not parse introspection query for the url '%s' (version: %s).", url, version)
        raise Exception("Could not parse introspection query for the url '%s' (version: %s)." % (url, version))

    if 'errors' in schema:
        for msg in schema['errors']:
            log.info("Received an error from %s (version: %s): %s", url, version, msg)
        return None

    # Catch 4** and 5** errors
    if response.status_code >= 400:
        log.info("Could not query schema from %s (version: %s).", url, version)
        return None

    # Got successful introspection response!
    log.info("Found the introspection response with '%s' version schema.", version)
    log.debug("The received introspection schema: %s", schema)

    if include_metadata:
        schema['__metadata__'] = {'spec_level': version}
        log.debug("Added metadata to introspection schema: %s", schema['__metadata__'])

    return schema


def query_introspection(url, headers=None, include_metadata=False, request_fn=None):
    """
    Send introspection query and get the GraphQL schema with the highest supported spec level.
    """
    log.debug("Introspection query about to be sent to '%s'.", url)

    for version in ('draft', 'oct2021', 'jun2018'):
        schema = query_introspection_version(url, headers=headers, version=version, include_metadata=include_metadata,
                                             request_fn=request_fn)
        if schema:
            return schema
        else:
            log.debug("Introspection query with '%s' version failed: %s", version, schema)

    # None of the introspection queries were successful
    log.warning("Introspection seems disabled for this endpoint: '%s'.", url)
    raise Exception("Introspection seems disabled for this endpoint: '%s'." % url)
