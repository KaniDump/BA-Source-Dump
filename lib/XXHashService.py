from typing import Union

from xxhash import xxh32_intdigest

def calculate_hash(name: Union[bytes, str]) -> int:
    if isinstance(name, str):
        name = name.encode('utf-8')
    return xxh32_intdigest(name, 0)
