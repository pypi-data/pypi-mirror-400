import sys

try:
    sys.modules[__name__] = __import__("finesse_virgo")
except ImportError:
    raise ImportError(
        "finesse_virgo package cannot be found. To use the Virgo specific tools please install the finesse_virgo package: pip install finesse_virgo"
    )
