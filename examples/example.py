from time import time
import array

import numpy as np

from pydivsufsort import divsufsort


random_string = np.random.randint(256, size=100_000, dtype=np.uint8)

print(divsufsort(b"banana"))
print(divsufsort(array.array("B", [98, 97, 110, 97, 110, 97])))
print(divsufsort(np.array([98, 97, 110, 97, 110, 97]).astype(np.uint8)))

d = time()
for _ in range(100):
    np.array(divsufsort(random_string))
print(time() - d)
