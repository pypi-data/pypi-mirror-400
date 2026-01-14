"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import builtins as bltn

BUILTIN_TYPES = tuple(
    getattr(bltn, _) for _ in dir(bltn) if isinstance(getattr(bltn, _), type)
)
