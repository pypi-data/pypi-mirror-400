import traceback

class WarnResult:
    def __init__(self, name, ok, output=None, error=None):
        self.name = name
        self.ok = ok
        self.output = output
        self.error = error

def safe_call(name, fn, *args, **kwargs):
    try:
        return WarnResult(
            name=name,
            ok=True,
            output=fn(*args, **kwargs)
        )
    except Exception as e:
        return WarnResult(
            name=name,
            ok=False,
            output=f"[WARN] {name} failed",
            error="".join(traceback.format_exception(e))
        )
