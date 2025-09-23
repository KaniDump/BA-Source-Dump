import time
from math import floor
from typing import List

class MersenneTwister:
    N: int = 624
    M: int = 397
    MATRIX_A: int = 0x9908B0DF
    UPPER_MASK: int = 0x80000000
    LOWER_MASK: int = 0x7FFFFFFF
    MAX_RAND_INT: int = 0x7FFFFFFF

    def __init__(self, seed: int = None) -> None:
        self.mt: List[int] = [0] * self.N
        self.mti: int = self.N + 1
        self.mag01: List[int] = [0, self.MATRIX_A]
        self.init_genrand(seed if seed is not None else int(time.time() * 1000))

    def init_genrand(self, s: int) -> None:
        self.mt[0] = s & 0xFFFFFFFF
        for mti in range(1, self.N):
            self.mt[mti] = (
                1812433253 * (self.mt[mti - 1] ^ (self.mt[mti - 1] >> 30)) + mti
            ) & 0xFFFFFFFF
        self.mti = self.N

    def next(self, min_value: int = None, max_value: int = None) -> int:
        if min_value is None:
            return (
                self.genrand_int31() if max_value is None else self.next(0, max_value)
            )
        if max_value is None:
            min_value, max_value = 0, min_value
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        return int(
            floor((max_value - min_value + 1) * self.genrand_real1() + min_value)
        )

    def next_float(self, include_one: bool = False) -> float:
        return self.genrand_real1() if include_one else self.genrand_real2()

    def next_double(self, include_one: bool = False) -> float:
        return self.genrand_real1() if include_one else self.genrand_real2()

    def next_bytes(self, length: int) -> bytes:
        return b''.join(
            self.genrand_int31().to_bytes(4, 'little') for _ in range(0, length, 4)
        )[:length]

    def genrand_int32(self) -> int:
        if self.mti >= self.N:
            self._twist()

        y = self.mt[self.mti]
        self.mti += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & 0xFFFFFFFF

    def _twist(self) -> None:
        for kk in range(self.N - self.M):
            y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
            self.mt[kk] = self.mt[kk + self.M] ^ (y >> 1) ^ self.mag01[y & 1]

        for kk in range(self.N - self.M, self.N - 1):
            y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
            self.mt[kk] = self.mt[kk + (self.M - self.N)] ^ (y >> 1) ^ self.mag01[y & 1]

        y = (self.mt[self.N - 1] & self.UPPER_MASK) | (self.mt[0] & self.LOWER_MASK)
        self.mt[self.N - 1] = self.mt[self.M - 1] ^ (y >> 1) ^ self.mag01[y & 1]
        self.mti = 0

    def genrand_int31(self) -> int:
        return self.genrand_int32() >> 1

    def genrand_real1(self) -> float:
        return self.genrand_int32() * (1.0 / 4294967295.0)

    def genrand_real2(self) -> float:
        return self.genrand_int32() * (1.0 / 4294967296.0)

    def genrand_real3(self) -> float:
        return (float(self.genrand_int32()) + 0.5) * (1.0 / 4294967296.0)

    def genrand_res53(self) -> float:
        a = self.genrand_int32() >> 5
        b = self.genrand_int32() >> 6
        return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0)
