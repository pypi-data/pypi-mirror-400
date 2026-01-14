import numpy as np
from copy import deepcopy
from finesse import constants


cpdef rebuild_model_settings(d) :
    """
    Rebuilds the model settings from a dictionary.

    Parameters
    ----------
    d : dict
        A dictionary where each key-value pair represents a setting name and its value.

    Returns
    -------
    ModelSettings
        A new `ModelSettings` object with its attributes set according to `d`.

    """
    s = ModelSettings()
    for k,v in d.items():
        setattr(s, k, v)
    return s


cdef class ModelSettings:
    """
    A class used to represent the settings of a model.

    Attributes
    ----------
    phase_config : PhaseConfig
        The configuration of the phase.
    homs_view : ndarray
        A view on the higher order modes (HOMs).
    max_n : int
        The maximum n value in the HOMs.
    max_m : int
        The maximum m value in the HOMs.
    num_HOMs : int
        The number of HOMs.
    lambda0 : float
        The wavelength.
    f0 : float
        The frequency, calculated as the speed of light divided by the wavelength.
    k0 : float
        The wave number, calculated as 2*pi divided by the wavelength.

    Methods
    -------
    __reduce__()
        Returns a tuple that can be used to rebuild the object using `rebuild_model_settings`.
    set_lambda0(value)
        Sets the wavelength and updates the frequency and wave number accordingly.
    """

    def __init__(self):
        self.phase_config = PhaseConfig()
        self.homs_view = None
        self.max_n = 0
        self.max_m = 0
        self.num_HOMs = 0
        self.set_lambda0(1064e-9)

    def __reduce__(self):
        """
        Returns a tuple that can be used to rebuild the object using `rebuild_model_settings`.

        Returns
        -------
        tuple
            A tuple containing the `rebuild_model_settings` function and a dictionary of the object's attributes.
        """
        # This is all to get around that memoryviews can't be deepcopied
        d = {"homs_view": np.asarray(self.homs_view)}
        d.update(
            {
                _: deepcopy(getattr(self, _))
                for _ in dir(self) if not _.startswith("__") and _ not in d and not callable(getattr(self, _))
            }
        )
        return rebuild_model_settings, (d,)

    @property
    def homs(self):
        """
        Returns a view on the higher order modes (HOMs).

        Returns
        -------
        ndarray
            A view on the HOMs.
        """
        return np.asarray(self.homs_view)

    @homs.setter
    def homs(self, value):
        """
        Sets the HOMs and updates the maximum n and m values and the number of HOMs.

        Parameters
        ----------
        value : ndarray
            The new HOMs.
        """
        self.homs_view = value
        self.max_n    = np.max(self.homs_view[:,0])
        self.max_m    = np.max(self.homs_view[:,1])
        self.num_HOMs = self.homs_view.shape[0]

    def set_lambda0(self, value):
        """
        Sets the wavelength and updates the frequency and wave number accordingly.

        Parameters
        ----------
        value : float
            The new wavelength.
        """
        self.lambda0 = value
        self.f0 = constants.C_LIGHT / self.lambda0
        self.k0 = 2.0 * constants.PI / self.lambda0


cdef class PhaseConfig:
    # TODO maybe this can be removed, not sure if it's used anywhere
    # other than in the model settings
    pass
