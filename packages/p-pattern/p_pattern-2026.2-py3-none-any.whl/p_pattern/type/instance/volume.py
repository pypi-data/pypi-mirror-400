"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

from p_pattern.type.instance.generic import instance_t as _base_t


class instance_t(_base_t):
    def Intersects(self, other: h.Self, max_overlap: float, /) -> bool:
        """"""
        bbox_1 = self.bbox
        bbox_2 = other.bbox
        if (
            (bbox_1.min_s[0] > bbox_2.max_s[0])
            or (bbox_2.min_s[0] > bbox_1.max_s[0])
            or (bbox_1.min_s[1] > bbox_2.max_s[1])
            or (bbox_2.min_s[1] > bbox_1.max_s[1])
            or (bbox_1.min_s[2] > bbox_2.max_s[2])
            or (bbox_2.min_s[2] > bbox_1.max_s[2])
        ):
            return False

        region_1 = self.region
        region_2 = other.region
        area_2 = other.area

        inter_min_row = max(bbox_1.min_s[0], bbox_2.min_s[0])
        inter_max_row = min(bbox_1.max_s[0], bbox_2.max_s[0])
        inter_min_col = max(bbox_1.min_s[1], bbox_2.min_s[1])
        inter_max_col = min(bbox_1.max_s[1], bbox_2.max_s[1])
        inter_min_dep = max(bbox_1.min_s[2], bbox_2.min_s[2])
        inter_max_dep = min(bbox_1.max_s[2], bbox_2.max_s[2])

        region_1_min_row = max(inter_min_row - bbox_1.min_s[0], 0)
        region_1_max_row = min(inter_max_row - bbox_1.min_s[0] + 1, region_1.shape[0])
        region_1_min_col = max(inter_min_col - bbox_1.min_s[1], 0)
        region_1_max_col = min(inter_max_col - bbox_1.min_s[1] + 1, region_1.shape[1])
        region_1_min_dep = max(inter_min_dep - bbox_1.min_s[2], 0)
        region_1_max_dep = min(inter_max_dep - bbox_1.min_s[2] + 1, region_1.shape[2])

        region_2_min_row = max(inter_min_row - bbox_2.min_s[0], 0)
        region_2_max_row = min(inter_max_row - bbox_2.min_s[0] + 1, region_2.shape[0])
        region_2_min_col = max(inter_min_col - bbox_2.min_s[1], 0)
        region_2_max_col = min(inter_max_col - bbox_2.min_s[1] + 1, region_2.shape[1])
        region_2_min_dep = max(inter_min_dep - bbox_2.min_s[2], 0)
        region_2_max_dep = min(inter_max_dep - bbox_2.min_s[2] + 1, region_2.shape[2])

        domain_1 = (
            slice(region_1_min_row, region_1_max_row),
            slice(region_1_min_col, region_1_max_col),
            slice(region_1_min_dep, region_1_max_dep),
        )
        domain_2 = (
            slice(region_2_min_row, region_2_max_row),
            slice(region_2_min_col, region_2_max_col),
            slice(region_2_min_dep, region_2_max_dep),
        )

        return self._RegionIntersects(domain_1, region_2, domain_2, area_2, max_overlap)
