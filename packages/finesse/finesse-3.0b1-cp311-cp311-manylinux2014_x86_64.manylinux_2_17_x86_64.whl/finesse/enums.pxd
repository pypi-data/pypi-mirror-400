"""
"""

"""Enum for the different types of modulator the Modulator component can represent.

am = Amplitude modulation
pm = Phase modulation
"""
cpdef enum ModulatorType:
    am
    pm
    # TODO ddb need to add in alignment and mode-matching modulator


"""Enum for the beamsplitter plane of incidence.

xz = x-z plane
yz = y-z plane
"""
cpdef enum PlaneOfIncidence:
    xz
    yz
