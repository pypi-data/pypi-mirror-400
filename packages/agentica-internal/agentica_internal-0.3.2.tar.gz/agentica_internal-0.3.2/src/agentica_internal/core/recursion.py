from sys import getrecursionlimit, setrecursionlimit

__all__ = ['no_recursion_limit']


################################################################################


class NoRecursionLimit:
    limit: int = 0
    count: int = 0

    def __init__(self):
        self.limit = 0
        self.count = 0

    def __enter__(self):
        self.count += 1
        if self.count == 1:
            self.limit = getrecursionlimit()
            setrecursionlimit(MAX_RECURSION_LIMIT)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.count -= 1
        if self.count == 0:
            setrecursionlimit(self.limit)


no_recursion_limit = NoRecursionLimit()


################################################################################

MAX_RECURSION_LIMIT = getrecursionlimit()
