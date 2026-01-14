"""
Physical constants module exposing a single named-tuple
which contains each of the constants values.

This tuple is imported in the top-level Finesse module - allowing
access to this structure with::

    from finesse import constants

    # get the speed of light for example
    c = constants.C_LIGHT

The table below lists all of the constants exposed in this module.

+-----------+------------------------------------+------------------------+
| Name      | Description                        | Exact value used       |
+===========+====================================+========================+
| `C_LIGHT` | The speed of light in m/s.         | 299792458.0            |
+-----------+------------------------------------+------------------------+
| `PI`      | Mathematical constant :math:`\pi`. | 3.14159265358979323846 |
+-----------+------------------------------------+------------------------+

"""
from collections import namedtuple
values = namedtuple("Constants", "PI C_LIGHT RAD2DEG DEG2RAD H_PLANCK")(_PI, _C_LIGHT, _RAD2DEG, _DEG2RAD, _H_PLANCK)
