"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from p_pattern.hint.number import number_h

interval_h = tuple[number_h, number_h]  # Closed interval.
precision_h = number_h | None  # None=infinite.

interval_with_precision_h = tuple[number_h, number_h, precision_h]
domain_precisions_h = precision_h | tuple[precision_h, ...]

domain_h = tuple[interval_h, ...]
domain_indexer_h = tuple[slice, ...]
chunked_domain_h = tuple[domain_h, tuple[interval_h, ...], domain_h]
