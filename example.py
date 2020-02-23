import numpy as np
from pydivsufsort import divsufsort

from time import time


print(divsufsort(b"banana"))


n = 10 ** 6
random_string = np.random.randint(256, size=n, dtype=np.uint8)
d = time()
divsufsort(random_string)
print(time() - d)

