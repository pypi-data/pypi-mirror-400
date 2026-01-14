"""Price Test

Aims to make price testing easier to implement.

Needs to consider:
    - Buckets
    - Hashing (likely?)
    - LookupTable
"""

from itertools import combinations
from typing import List, Set

from .lookuptable import LookupTable


class Bucket:
    def __init__(self, a):
        self.bucket = a
        self.count = 0
        self.values = set()

    def __repr__(self):
        return f"Bin: {self.bucket}, Count: {self.count}, Set: {self.values}"

    def put(self, val):
        self.values.add(val)
        self.count += 1


class PriceTest:

    def __init__(self, by: str, ratetable: LookupTable):

        self.by = by
        self.ratetable = ratetable

        self.num_buckets = len(ratetable)
        self.buckets = {i: Bucket(i) for i in range(self.num_buckets)}

        self.get = lambda q: by(q) if callable(by) else q[by]
        self.bin = staticmethod(self.get_bin_function())

    def __iter__(self):
        return iter(self.buckets)

    def __contains__(self, v):
        for s in self.buckets.values():
            if v in s:
                return True
        return False

    def __getitem__(self, quote):
        return self.apply(quote)

    def __call__(self, quote):
        return self.apply(quote)

    def apply(self, quote):

        val = self.get(quote)
        bucket = self.bin(quote)

        self.buckets[bucket].values.add(val)
        self.buckets[bucket].count += 1

        return self.ratetable.lookup(bucket)

    def unique_bucket_values(self) -> bool:
        bucket_sets: List[Set] = [b.values for b in self.buckets.values()]

        for a, b in combinations(bucket_sets, 2):

            if len(a.intersection(b)) > 0:
                return False

        return True

    def get_bin(self, v):
        return self.bin(v)

    def get_bucket(self, v):
        return self.buckets[self.bin(v)]

    def get_bin_function(self):
        buckets = len(self.buckets)

        def bin_func(q):
            val = self.get(q)
            bucket = hash(val) % buckets
            return bucket

        return bin_func
