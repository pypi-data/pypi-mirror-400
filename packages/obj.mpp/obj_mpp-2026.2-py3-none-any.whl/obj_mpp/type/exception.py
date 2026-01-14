"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from obj_mpp.constant.interface.message import SNH_MSG


class ShouldNeverHappenError(Exception):
    pass


def ShouldNeverHappenException(message: str | None = None) -> ShouldNeverHappenError:
    """
    Do not prefix argument with "*, " since it imposes to always call with "message = ".
    """
    if message is None:
        message = SNH_MSG
    else:
        message = f"{message}: {SNH_MSG}"

    return ShouldNeverHappenError(message)
