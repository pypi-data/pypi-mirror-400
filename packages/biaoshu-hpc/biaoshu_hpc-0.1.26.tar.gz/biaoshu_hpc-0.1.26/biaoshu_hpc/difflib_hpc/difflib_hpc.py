from difflib import SequenceMatcher, Match, Differ
from typing import List, Tuple

from . import longest_common_substring

lcs = longest_common_substring.LongestCommonSubstring()


class HpcSequenceMatcher(SequenceMatcher):

    def __init__(self, isjunk=None, a='', b='', autojunk=True):
        assert isjunk is None, "isjunk is not supported in hpc version"
        super().__init__(isjunk=None, a=a, b=b, autojunk=autojunk)

    def get_matching_blocks(self) -> List[Match]:
        if self.matching_blocks is not None:
            return self.matching_blocks

        non_adjacent: List[Tuple[int, int, int]] = calculate_match_block(a=self.a, b=self.b)

        self.matching_blocks = list(map(Match._make, non_adjacent))

        return self.matching_blocks

class HpcDiffer(Differ):

    def compare(self, a, b):
        cruncher = HpcSequenceMatcher(None, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if tag == "replace":
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            elif tag == "delete":
                g = self._dump("-", a, alo, ahi)
            elif tag == "insert":
                g = self._dump("+", b, blo, bhi)
            elif tag == "equal":
                g = self._dump(" ", a, alo, ahi)
            else:
                raise ValueError("unknown tag %r" % (tag,))

            yield from g

def calculate_match_block(a: str | List[str], b: str | List[str]) -> List[Tuple[int, int, int]]:
    if isinstance(a, str) and isinstance(b, str):
        return lcs.calculate_for_string(str1=a, str2=b)
    elif isinstance(a, list) and isinstance(b, list):
        return lcs.calculate_for_string_list(list1=a, list2=b)
    else:
        raise TypeError("Input must be either string or list")
