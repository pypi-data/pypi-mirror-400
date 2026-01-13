"""
Tools for calculating entrainment and degassing
"""

import numpy as np
from ..runinfo import Interval, Snapshot


def largest_label(snapshot: Snapshot) -> int:
    """
    Get the label of the largest bubble, typically assumed to be the sky
    """
    return np.argmax(snapshot.get_volume_vector()).item()


def get_entrained_volumes(
        interval: Interval,
        sky_label_start: None | int = None,
        sky_label_end: None | int = None,
        v_min: float = 0.0
        ) -> np.ndarray:
    r"""
    Get the volumes associated with entrainment events over the interval

    :param interval: Interval :math:`t\in[t^{n}, t^{n+1}]` over which to extract entrainment events
    :param sky_label_start: Label of the sky at :math:`t^{n}`. If not provided, calculated using `largest_label()`
    :param sky_label_end: Label of the sky at :math:`t^{n+1}`. If not provided, calculated using `largest_label()`
    :param v_min: Minimum volume to report, :math:`v_{\text{min}}`. Default is `0.0`.
    :return: The volume of all entrainment events where :math:`v_{\text{entrained}}>v_{\text{min}}`
    """

    # figure out sky labels if not specified
    if sky_label_start is None:
        sky_label_start = largest_label(interval.start)
    if sky_label_end is None:
        sky_label_end = largest_label(interval.end)

    # get column corresponding to entrainment
    vent = interval.get_vtm(normalize=False).getcol(sky_label_start)

    # ignore volume that stays in the sky
    vent[sky_label_end, 0] = 0

    # convert to an array
    vent = vent.toarray()

    # remove under resolved bubbles
    return vent[(vent > v_min)]


def get_degassed_volumes(
        interval: Interval,
        sky_label_start: None | int = None,
        sky_label_end: None | int = None,
        v_min: float = 0.0
        ) -> np.ndarray:
    r"""
    Get the volumes associated with degassing events over the interval

    :param interval: Interval :math:`t\in[t^{n}, t^{n+1}]` over which to extract entrainment events
    :param sky_label_start: Label of the sky at :math:`t^{n}`. If not provided, calculated using `largest_label()`
    :param sky_label_end: Label of the sky at :math:`t^{n+1}`. If not provided, calculated using `largest_label()`
    :param v_min: Minimum volume to report, :math:`v_{\text{min}}`. Default is `0.0`.
    :return: The volume of all degassing events where :math:`v_{\text{degassed}}>v_{\text{min}}`
    """

    # figure out sky labels if not specified
    if sky_label_start is None:
        sky_label_start = largest_label(interval.start)
    if sky_label_end is None:
        sky_label_end = largest_label(interval.end)

    # get column corresponding to entrainment
    vdg = interval.get_vtm(normalize=False).getrow(sky_label_end)

    # ignore volume that stays in the sky
    vdg[0, sky_label_start] = 0

    # convert to an array
    vdg = vdg.toarray()

    # remove under resolved bubbles
    return vdg[(vdg > v_min)]
