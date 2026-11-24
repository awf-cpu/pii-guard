import sys

from .core import mask

if __name__ == "__main__":
    print(mask(sys.stdin.read()).text, end="")
