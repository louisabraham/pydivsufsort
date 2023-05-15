import numpy as np
from collections import namedtuple

from . import (
    divsufsort,
    sa_search,
    kasai,
    lcp_segtree,
    lcp_query,
    most_frequent_substrings,
)
from .stringalg import _common_substrings

SearchResult = namedtuple("SearchResult", ("count", "position"))

MFSResult = namedtuple("MFSResult", ("positions", "counts"))


def cast_to_numpy(inp, copy=True):
    if isinstance(inp, str):
        try:
            inp = inp.encode("ascii")
        except UnicodeEncodeError:
            raise TypeError("str must only contain ascii chars")
    if isinstance(inp, bytes):
        inp = np.frombuffer(inp, dtype=np.uint8)
    return np.ascontiguousarray(np.array(inp, copy=copy))


class WonderString:
    def __init__(self, inp, copy=True):
        self.string = cast_to_numpy(inp, copy)
        self.itemsize = self.string.dtype.itemsize

    @property
    def bytes(self):
        if not hasattr(self, "_bytes"):
            if self.string.dtype == np.uint8:
                self._bytes = self.string
            else:
                self._bytes = self.string.view("uint8")
        return self._bytes

    @property
    def suffix_array_bytes(self):
        if not hasattr(self, "_suffix_array_bytes"):
            self._suffix_array_bytes = divsufsort(self.bytes)
        return self._suffix_array_bytes

    @property
    def suffix_array(self):
        if not hasattr(self, "_suffix_array"):
            if self.itemsize == 1:
                self._suffix_array = self.suffix_array_bytes
            else:
                self._suffix_array = np.ascontiguousarray(
                    self.suffix_array_bytes[
                        self.suffix_array_bytes % self.itemsize == 0
                    ]
                    // self.itemsize
                )
        return self._suffix_array

    def search(self, pattern, return_positions=False):
        if self.itemsize != 1:
            raise NotImplementedError(
                "Not supported for non byte strings.\n"
                "Please raise an issue on "
                "<https://github.com/louisabraham/pydivsufsort/issues>"
            )

        ans = SearchResult(*sa_search(self.string, self.suffix_array, pattern))

        if return_positions:
            if not ans.count:
                return self.suffix_array[:0]
            return self.suffix_array[ans.position : ans.position + ans.count]
        return ans

    @property
    def lcp_array(self):
        if not hasattr(self, "_lcp_array"):
            self._lcp_array = kasai(self.string, self.suffix_array)
        return self._lcp_array

    @property
    def _lcp_segtree(self):
        if not hasattr(self, "__lcp_segtree"):
            self.__lcp_segtree = lcp_segtree(
                self.string, self.suffix_array, self.lcp_array
            )
        return self.__lcp_segtree

    def lcp(self, *args):
        if len(args) == 1:
            return lcp_query(self._lcp_segtree, args[0])
        elif len(args) == 2:
            return lcp_query(self._lcp_segtree, [args])[0]

    def most_frequent_substrings(self, length, limit=0, minimum_count=1):
        """
        Parameters
        ----------

        lcp : np.ndarray
            LCP array
        length : int
            length of the substrings to compare
        limit : int (default 0)
            number of substrings to extract, 0 for all of them
        minimum_count : int (default 1)
            ignore the substrings that occur less than `minimum_count` times


        Returns
        -------
        positions : np.ndarray
            position in the string
        counts : np.ndarray
            number of occurrences, decreasing
        """
        pos, cnt = most_frequent_substrings(
            self.lcp_array, length, limit, minimum_count
        )
        return MFSResult(self.suffix_array[pos], cnt)


def common_substrings(s1, s2, limit=25):
    """All common substrings of length more than limit.

    Parameters
    ----------

    s1 : string or np.ndarray
    s2 : string or np.ndarray
    limit : int (default 25)

    Returns
    -------

    result : list of tuples
        (idx1, idx2, length) where idx1 and idx2 are positions in s1 and s2
        length >= limit and the pairs are sorted by (idx1, idx2)
    """
    # TODO: in Cython 0.30, use fused types to avoid casting
    s1 = cast_to_numpy(s1)
    s2 = cast_to_numpy(s2)
    sep = max(s1.max(), s2.max()) + 1
    s = np.empty(len(s1) + len(s2) + 1, dtype=np.result_type(s1[0], s2[0], sep))
    s[: len(s1)] = s1
    s[len(s1)] = sep
    s[len(s1) + 1 :] = s2
    suffix_array = divsufsort(s)
    lcp = kasai(s, suffix_array)
    return _common_substrings(
        suffix_array.astype(np.uint64), lcp.astype(np.uint64), len(s1), limit
    )
