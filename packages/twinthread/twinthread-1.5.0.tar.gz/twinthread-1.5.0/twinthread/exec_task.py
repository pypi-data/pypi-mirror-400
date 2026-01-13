import contextlib


@contextlib.contextmanager
def capture():
    import sys
    from io import StringIO

    oldout, olderr = sys.stdout, sys.stderr
    try:
        out = [StringIO(), StringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def exec_code(code, client):
    error = None

    with capture() as out:
        try:
            result = exec(code, {"client": client})
        except Exception as e:
            error = e

    return {"output": out[0], "errors": out[1] if error is None else str(error)}
