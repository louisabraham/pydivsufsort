from pathlib import Path
from subprocess import Popen


script = Path(__file__).parent / "test.sh"
path = str(script.absolute()).replace("\\", r"\\")
print(path)
Popen(["bash.exe", "-c", path]).wait()
