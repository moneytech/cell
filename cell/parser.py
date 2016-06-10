
from cell.peekablestream import PeekableStream


def _parse_symbol(tokens):
    token = tokens.next
    if token is None:
        raise Exception("Expecting the name of symbol.")
    typ, val = token

    tokens.move_next()
    if typ == "symbol":
        return ("symbol", val)
    else:
        raise Exception(
            "Only symbols are allowed in function parameter lists."
            + " I found:" + str(token) + "."
        )


def _parse_params(tokens):
    ret = []
    if tokens.next[0] != ":":
        return ret
    tokens.move_next()
    typ = tokens.next[0]
    if typ != "(":
        raise Exception("Colon must be followed by ( in a function definition.")
    tokens.move_next()
    typ = tokens.next[0]
    if typ != ")":
        while typ != ")":
            ret.append(_parse_symbol(tokens))
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "A function parameter list ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse_commands(tokens):
    ret = []
    if tokens.next is None:
        raise Exception("A function definition ran off the end of the program.")
    typ = tokens.next[0]
    if typ != "}":
        while typ != "}":
            p = _parse(None, tokens, ";}")
            if p is not None:
                ret.append(p)
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "A function definition ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse_args(tokens):
    ret = []
    if tokens.next is None:
        raise Exception("An argument list ran off the end of the program.")
    typ = tokens.next[0]
    if typ != ")":
        while typ != ")":
            ret.append(_parse(None, tokens, ",)"))
            typ = tokens.next[0]
            tokens.move_next()
            if tokens.next is None:
                raise Exception(
                    "An argument list ran off the end of the program.")
    else:
        tokens.move_next()
    return ret


def _parse(expr, tokens, stop_at):
    token = tokens.next
    if token is None:
        return expr
    typ, val = token
    if typ in stop_at:
        return expr

    tokens.move_next()
    if typ in ("number", "string", "symbol") and expr is None:
        return _parse((typ, val), tokens, stop_at)
    elif typ == "operation":
        nxt = _parse(None, tokens, stop_at)
        return _parse(("operation", val, expr, nxt), tokens, stop_at)
    elif typ == "(":
        args = _parse_args(tokens)
        return _parse(("call", expr, args), tokens, stop_at)
    elif typ == "{":
        params = _parse_params(tokens)
        commands = _parse_commands(tokens)
        return _parse(("function", params, commands), tokens, stop_at)
    elif typ == "=":
        if expr[0] != "symbol":
            raise Exception("You can't assign to anything except a symbol.")
        nxt = _parse(None, tokens, stop_at)
        return _parse(("assignment", expr, nxt), tokens, stop_at)
    else:
        raise Exception("Unexpected token: " + str(token))


def parse(tokens_iterator):
    tokens = PeekableStream(tokens_iterator)
    while tokens.next is not None:
        p = _parse(None, tokens, ";")
        if p is not None:
            yield p
        tokens.move_next()