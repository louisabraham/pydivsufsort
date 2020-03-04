from time import time
import array

import numpy as np

from pydivsufsort import divsufsort


print(divsufsort(b"banana"))
print(divsufsort(array.array("B", [98, 97, 110, 97, 110, 97])))
print(divsufsort(np.array([98, 97, 110, 97, 110, 97]).astype(np.uint8)))


n = 1_000_000

random_string = np.random.randint(255, size=n, dtype=np.uint8)

d = time()
divsufsort(random_string)
print(time() - d)

random_string = random_string.astype(np.uint64)

d = time()
divsufsort(random_string)
print(time() - d)

random_string[0] = -1

d = time()
divsufsort(random_string)
print(time() - d)
