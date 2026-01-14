# `3.0a27`

A new Finesse version was released on PyPi and conda-forge. We recommend keeping up to date as much as possible.

## Changes

- Allow detectors and ports to be visualized with component_tree method. See an example in the [docs](https://finesse.ifosim.org/docs/develop/usage/python_api/models_and_components.html#visualizing-the-model)
- Fix `finesse.gaussian.HGMode` ignoring shape of the given y vector when n=m.
- Option to keep only a subset of symbols in symbolic `Model.ABCD` method
- Add options to specify the plane of incidence for a beamsplitter and to misalign a beamsplitter
