import inspect, json, os
from datetime import datetime
from loguru import logger

def debug_var(value, path=None, active=True):
    if not active:
        return
    f = inspect.stack()[1]
    fn, ln = f.function, f.lineno
    cls = type(f.frame.f_locals["self"]).__name__ if "self" in f.frame.f_locals else "global"
    try:
        line = f.code_context[0]
        var = line.split("debug_var(", 1)[1].split(",", 1)[0].strip().replace(")", "")
    except Exception:
        var = "value"
    if path is None:
        ts = datetime.now().strftime("%Y%m%d-%H")
        path = f"tmp/{cls}-{fn}-{var}-{ts}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        file = path + ".json"
        with open(file, "w", encoding="utf-8") as w:
            json.dump(value, w, indent=2, ensure_ascii=False)
        fmt = "json"
    except Exception:
        file = path + ".txt"
        with open(file, "w", encoding="utf-8") as w:
            w.write(repr(value))
        fmt = "text"
    logger.debug(f"DEBUG | var='{var}' | class='{cls}' | function='{fn}' | line={ln} | format={fmt} | path='{file}'")
    return file

def debug_var_v2(value, path=None, active=True):
    if not active:
        return
    f = inspect.stack()[1]
    fn, ln = f.function, f.lineno
    cls = type(f.frame.f_locals["self"]).__name__ if "self" in f.frame.f_locals else "global"
    try:
        line = f.code_context[0]
    except Exception:
        var = "value"
    if path is None:
        ts = datetime.now().strftime("%Y%m%d-%H")
        path = f"tmp/{cls}-{fn}-{line}-{ts}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        file = path + ".json"
        with open(file, "w", encoding="utf-8") as w:
            json.dump(value, w, indent=2, ensure_ascii=False)
        fmt = "json"
    except Exception:
        file = path + ".txt"
        with open(file, "w", encoding="utf-8") as w:
            w.write(repr(value))
        fmt = "text"
    logger.debug(f"DEBUG | var='{var}' | class='{cls}' | function='{fn}' | line={ln} | format={fmt} | path='{file}'")
    return file