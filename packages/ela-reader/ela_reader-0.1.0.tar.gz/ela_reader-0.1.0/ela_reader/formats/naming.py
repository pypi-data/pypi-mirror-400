"""
Get output filenames following the conventions from flexELA
"""


def vtm_filename(n: int) -> str:
    r"""
    Returns the standard filename for the
    [volume tracking matrix](https://flexela-docs.pages.dev/api/OutputFiles#volmetrackingmatrix) (VTM)
    :math:`\boldsymbol{Q}^{(n-1\, \rightarrow \,n)}`
    """
    return f"afwd_{n:0>6d}.bin"


def volume_vector_filename(n: int) -> str:
    r"""
    Returns the standard filename for [volume vector](https://flexela-docs.pages.dev/api/OutputFiles#volumevector)
    :math:`\vec{v}^n `
    """
    return f"v_{n:0>6d}.bin"


def timelog_filename() -> str:
    r"""
    Returns the standard filename for the [binary log file](https://flexela-docs.pages.dev/api/OutputFiles#timelogbin)
    """
    return "timelog.bin"


def tracking_filename() -> str:
    r"""
    Returns the standard filename for the [ASCII log file](https://flexela-docs.pages.dev/api/OutputFiles#trackinglog)
    """
    return "tracking.log"
