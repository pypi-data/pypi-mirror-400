"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from p_pattern.extension.type import number_h

coordinate_h = number_h
position_h = tuple[coordinate_h, ...]
position_1_h = tuple[coordinate_h]
position_2_h = tuple[coordinate_h, coordinate_h]
position_3_h = tuple[coordinate_h, coordinate_h, coordinate_h]
