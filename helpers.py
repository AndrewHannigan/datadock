from sqlparse.tokens import Token
import sqlparse
import logging


def is_flag_comment(token: Token, flag: str):
    return hasattr(token, 'value') \
           and token.ttype == Token.Comment.Single \
           and token.value[:len(flag)] == flag


def extract_flag_comment(sql: str, flag: str):
    assert flag[:2] == '--'

    stmt = sqlparse.parse(sql)[0]
    comments = [t for t in stmt.flatten() if t.ttype == Token.Comment.Single]
    logging.debug("Comments found: {}".format(comments))

    flag_comments = [t for t in comments if is_flag_comment(t, flag)]

    if not flag_comments:
        raise ValueError("No {} comment found in stmt".format(flag))

    value = flag_comments[0].value[len(flag):].strip()
    return value


# TODO: Check that every column has a --type flag
def extract_type_annotations(sql: str):
    stmt = sqlparse.parse(sql)[0]
    comments = [t for t in stmt.flatten() if t.ttype == Token.Comment.Single]
    logging.debug("Comments found: {}".format(comments))

    cols = {}
    for t in comments:
        if is_type_comment(t):
            attribute = get_attribute_ancestor(t)
            col_type = t.value.replace('--type', '').strip()
            col_name = attribute.get_name()

            if col_name in cols:
                raise ValueError(
                    "Multiple type annotations found for "
                    "column named {}".format(col_name)
                )

            cols[col_name] = col_type

    return cols


def is_type_comment(token: Token):
    # Is it contained in an Attribute token?
    attribute = get_attribute_ancestor(token)
    if not attribute:
        logging.debug(
            "{} is not a descendant of a sqlparse.sql.Identifier, "
            "so it is not a type comment.".format(token)
        )
        return False

    if not token.value[:6] == '--type':
        logging.debug(
            "Comment '{}' does not start with '--type', "
            "so it is not a type comment.".format(token)
        )
        return False

    logging.debug("Comment '{}' identified as a type comment.".format(token))
    return True


def get_attribute_ancestor(token: Token):
    # Returns None if no Attribute ancestor found
    cur = token.parent

    while cur:
        if isinstance(cur, sqlparse.sql.Identifier):
            return cur
        else:
            cur = cur.parent

    return None
