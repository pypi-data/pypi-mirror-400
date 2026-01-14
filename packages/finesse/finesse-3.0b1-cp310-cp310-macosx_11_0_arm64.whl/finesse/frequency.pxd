cdef class Frequency:
    cdef:
        str __name
        bint __is_audio, __symbol_changing
        int __order
        int __carrier
        int __index
        object __symbol
        object __lambdified
        double __start_value
        Frequency __carrier_obj


"""This struct is used to contain various properties of a frequency bin in
a simulation in a fast C struct. The python side should update this struct
and pass it to C functions, allowing GIL to be released, etc.
"""
cdef struct frequency_info:
    double f # Current frequency bin value [Hz]
    double *f_car # If a sideband, the current carrier frequency bin value [Hz]
    Py_ssize_t index # Index of this frequency bin
    # Optical carrier field members
    Py_ssize_t audio_lower_index # index of lower sideband if signals being simulated
    Py_ssize_t audio_upper_index # index of upper sideband if signals being simulated
    # Optical signal field members
    Py_ssize_t audio_order # audio order, either -1 or +1, 0 means a carrier
    Py_ssize_t audio_carrier_index # index of carrier frequency bin


ctypedef frequency_info frequency_info_t


cdef class FrequencyContainer:
    cdef readonly:
        Py_ssize_t size
        tuple frequencies
    cdef:
        frequency_info_t* frequency_info
        frequency_info_t* carrier_frequency_info

    cdef update_frequency_info(self)
    cdef initialise_frequency_info(self)
