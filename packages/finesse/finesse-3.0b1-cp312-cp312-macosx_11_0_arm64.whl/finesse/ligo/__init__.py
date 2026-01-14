import sys

try:
    sys.modules[__name__] = __import__("finesse_ligo")
except ImportError:
    raise ImportError(
        "finesse_ligo package cannot be found. To use the LIGO specific tools please install the finesse_ligo package: pip install finesse_ligo"
    )
