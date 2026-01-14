"""Frequency analysis tools."""

import numpy as np

from finesse.element import ModelElement
from finesse.parameter import float_parameter
from finesse.symbols import Symbol
from finesse.components.general import unique_element

from libc.stdlib cimport free, calloc

cdef class FrequencyContainer:
    """Contains an array of frequency objects and their associated faster access C
    struct information."""
    def __cinit__(self, *args, **kwargs):
        self.size = 0
        self.frequency_info = NULL
        self.carrier_frequency_info = NULL

    def __init__(self, frequencies, FrequencyContainer carrier_cnt=None):
        self.size = len(frequencies)
        self.frequencies = tuple(frequencies)
        if self.frequency_info != NULL:
            raise MemoryError()
        self.frequency_info = <frequency_info_t*> calloc(self.size, sizeof(frequency_info_t))
        if not self.frequency_info:
            raise MemoryError()
        if carrier_cnt:
            if not carrier_cnt.frequency_info:
                raise MemoryError()
            self.carrier_frequency_info = carrier_cnt.frequency_info
        else:
            self.carrier_frequency_info = NULL

    def __dealloc__(self):
        if self.size:
            free(self.frequency_info)

    def get_info(self, Py_ssize_t index):
        if not (0 <= index <= self.size):
            raise IndexError()
        rtn = {
            "f" : self.frequency_info[index].f,
            "index" : self.frequency_info[index].index,
            "audio_lower_index" : self.frequency_info[index].audio_lower_index,
            "audio_upper_index" : self.frequency_info[index].audio_upper_index,
            "audio_order" : self.frequency_info[index].audio_order,
            "audio_carrier_index" : self.frequency_info[index].audio_carrier_index,
        }
        return rtn

    cdef initialise_frequency_info(self) :
        cdef Py_ssize_t i, cidx

        for i in range(self.size):
            self.frequency_info[i].f = <double>self.frequencies[i].f
            self.frequency_info[i].index = <Py_ssize_t>self.frequencies[i].index
            self.frequency_info[i].audio_order = <int>self.frequencies[i].audio_order

            if self.frequency_info[i].audio_order:
                assert(self.carrier_frequency_info)
                cidx = <Py_ssize_t>self.frequencies[i].audio_carrier_index
                self.frequency_info[i].audio_carrier_index = cidx
                self.frequency_info[i].f_car = &self.carrier_frequency_info[cidx].f
                # Update carrier info so it knows about this sideband
                if self.frequency_info[i].audio_order == 1:
                    self.carrier_frequency_info[cidx].audio_upper_index = <Py_ssize_t>self.frequencies[i].index
                elif self.frequency_info[i].audio_order == -1:
                    self.carrier_frequency_info[cidx].audio_lower_index = <Py_ssize_t>self.frequencies[i].index
                else:
                    raise Exception("Unexpected")

        # if self.is_audio:
        #     for i in range(len(self.unique_fcnt)):
        #         fcnt = self.unique_fcnt[i]
        #         for j in range(fcnt.size):
        #             fcnt.frequency_info[j].f = <double>fcnt.frequencies[j].f
        #             fcnt.frequency_info[j].index = <Py_ssize_t>fcnt.frequencies[j].index

    cdef update_frequency_info(self) :
        """Updates the values of all frequencies in the c-type frequency_info struct."""
        cdef Py_ssize_t i

        for i in range(self.size):
            self.frequency_info[i].f = <double>self.frequencies[i].f

    def get_frequency_index(self, value):
        """For a given value (either float or symbolic) return the index of the
        frequency with the same value.

        Parameters
        ----------
        value : [number | symbolic]
            Frequency value to test for

        Returns
        -------
        index : int
            Index for this frequency container
        """
        try:
            frequency = float(value)
        except TypeError:
            frequency = float(value.value)
        # find the right frequency index
        for freq in self.frequencies:
            if freq.f == frequency:
                f_idx = freq.index
                break
        if f_idx is None:
            raise RuntimeError(
                f"Could not find a frequency with a value of {frequency} Hz ({value!r})"
            )
        return f_idx

def generate_frequency_list(model):
    """For a given model a symbolic list of frequencies is generated. The result can be
    used to generate a set of frequencies bins to be modelled in a simulation.

    This method relies on using :class:`.Symbol`. Using symbolic statements this method
    attempts to isolate uniqe frequency bins whilst leaving those changing during a
    simulation present.

    Returns
    -------
    List of :class:`.Symbol`
    """

    def unique_indices(arr):
        """Simple unique element finder which doesn't require any greater or less than
        operations, this isn't tuned for efficiency at all."""
        lst = list(arr)
        lst2 = list(arr)
        for i in range(len(lst)):
            if lst.count(lst2[i]) > 1:
                lst[i] = None

        return [_ for _, __ in enumerate(lst) if __ is not None]

    fn_eval = np.vectorize(lambda x: x.eval())
    fn_eval2 = np.vectorize(lambda x: x.eval(keep_changing_symbols=True))
    # fn_subs = np.vectorize(
    #     lambda x, **kwargs: x.eval(keep_changing_symbols=True, subs=kwargs)
    # )
    fn_is_changing = np.vectorize(lambda x: x.is_changing)

    source_frequencies = []
    source_components = []
    modulation_frequencies = []

    for comp in model._frequency_generators:
        s = comp._source_frequencies()
        source_frequencies.extend(s)
        source_components.extend((comp,) * len(s))

        m = comp._modulation_frequencies()
        modulation_frequencies.extend(m)

    # Now to prune the frequency list
    Nm = len(modulation_frequencies)
    Ns = len(source_frequencies)

    if Ns == 0:
        raise Exception("There are no source frequencies present in the model")

    if Nm == 0:
        Fsym = np.array(source_frequencies)
    else:
        # First we make a list with all possible combinations of frequencies
        Fsym = (
            np.vstack((np.atleast_2d(modulation_frequencies),) * Ns)
            + np.hstack((np.atleast_2d(source_frequencies).T,) * Nm)
        ).flatten()
        Fsym = np.hstack((source_frequencies, Fsym))

    # Take all the frequency values which definitely won't be changing
    not_changing = Fsym[np.bitwise_not(fn_is_changing(Fsym))]
    if len(not_changing) == 0:
        not_changing = []
    else:
        # ... and select all those which are unique
        _, idx, _, _ = np.unique(fn_eval(not_changing), True, True, True)
        not_changing = not_changing[idx]

    # First select only the changing frequency bins
    changing = Fsym[fn_is_changing(Fsym)]
    if len(changing) == 0:
        changing = []
    else:
        # We need to use a different unique finding function that doesn't rely on
        # using > or < than comparisons like np.unique. I'm not sure how to implement
        # > and < for Symbols sensibly
        idx = unique_indices(fn_eval2(changing))
        changing = changing[idx]

    # Finally sort the indicies so that upper and lower sidebands are grouped together. This
    # help with numerical errors when iterating outputs later so that similarly sized elements are
    # grouped this isn't always true though, just generally in regards to upper and lower sidebands.
    final = np.hstack((changing, not_changing))
    srt_idx = np.argsort(abs(fn_eval(final)))
    return final[srt_idx]


@unique_element() # only one fsig per model
@float_parameter("f", "Signal frequency", units="Hz", validate="_validate_fsig", is_default=True)
class Fsig(ModelElement):
    """This element represents the signal frequency (``fsig``) used in a model. It is a
    unique element, which means only one can be added to any given model. This is done
    automatically with the name ``fsig``. It has a single parameter ``f`` for the
    frequency of the signal.

    The signal frequency must be set by the user to enable transfer functions and noise
    projections to be simulated.

    Parameters
    ----------
    name : str
        Name of this element
    f : [float|None]
        Signal frequency to use in a model [Hz]. If set to ``None`` then no signal
        frequencies will be modelled in the simulation.
    """
    def __init__(self, name, value):
        super().__init__(name)
        self.f = value

    def _validate_fsig(self, value):
        if value is None or isinstance(value, Symbol):
            return value
        elif value <= 0:
            raise Exception("fsig value must be > 0 Hz")
        else:
            return value


cdef class Frequency:
    """Represents a frequency "bin" with a specific index.

    The value of the frequency is calculated from the name of the frequency.

    Parameters
    ----------
    name : str
        Name of the frequency.

    order : int, optional
        The order of the frequency, defaults to zero.
    """
    def __init__(
        self,
        name,
        symbol,
        *,
        index=None,
        audio=False,
        audio_carrier_index=None,
        audio_carrier_object=None,
        audio_order=0,
    ):
        self.__name = name
        self.__symbol = symbol
        self.__index = index
        self.__is_audio = audio
        self.__symbol_changing = symbol.is_changing
        self.__start_value = self.__symbol.eval()
        self.__lambdified = self.__symbol.lambdify()

        if audio:
            if audio_carrier_index is None:
                raise Exception("Audio frequency carrier must be specified")

            if audio_order not in (-1, 1):
                raise Exception("Audio frequency order must be -1 or +1")

            self.__order = audio_order
            self.__carrier = audio_carrier_index
            self.__carrier_obj = audio_carrier_object
        else:
            self.__order = 0
            self.__carrier = 0

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.name} (f={self.symbol}={self.f}) at "
            f"{ hex(id(self)) }>"
        )

    def __str__(self):
        return f"<{self.name} is {self.f}Hz (Frequency)>"

    def __deepcopy__(self, memo):
        raise Exception(
            "Frequency objects cannot be deepcopied as they are associated with Simulations"
        )

    @property
    def symbol(self):
        return self.__symbol

    @property
    def f(self):
        if self.__symbol_changing:
            return self.__lambdified()
        else:
            return self.__start_value

    @property
    def is_audio(self):
        """Is this an audio sideband frequency?"""
        return self.__is_audio

    @property
    def audio_carrier_index(self):
        """The carrier frequency.

        :`getter`: Returns the carrier frequency index (read-only).
        """
        return self.__carrier

    @property
    def name(self):
        """Name of the frequency object.

        :`getter`: Returns the name of the frequency (read-only).
        """
        return self.__name

    @property
    def audio_order(self):
        """Audio modulation order of this frequency.

        :`getter`: Returns the order of the frequency (read-only).
        """
        return self.__order

    @property
    def index(self):
        """Index of the frequency object.

        :`getter`: Returns the index of the frequency (read-only).
        """
        return self.__index

    @property
    def audio_carrier(self):
        """Frequency object for the carrier frequency of this sideband, if it is a
        sideband.

        :`getter`: Returns the index of the frequency (read-only).
        """
        if self.__is_audio:
            return self.__carrier_obj
        else:
            return None
