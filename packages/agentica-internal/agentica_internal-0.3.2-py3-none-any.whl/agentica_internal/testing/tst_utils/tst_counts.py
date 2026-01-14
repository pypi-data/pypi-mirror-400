from typing import Self

from ...core.color import DIM, RED

__all__ = [
    'TestCounts',
]


class TestCounts:
    num_pass = 0
    num_fail = 0
    num_new = 0
    num_err = 0

    def __init__(self, num_pass: int = 0, num_fail: int = 0, num_new: int = 0, num_err: int = 0):
        self.num_pass = num_pass
        self.num_fail = num_fail
        self.num_new = num_new
        self.num_err = num_err

    def reset(self):
        self.num_pass = 0
        self.num_fail = 0
        self.num_new = 0
        self.num_err = 0

    def add_from(self, other: Self):
        self.num_pass += other.num_pass
        self.num_fail += other.num_fail
        self.num_new += other.num_new
        self.num_err += other.num_err

    def nonpassing_count(self) -> int:
        return self.num_fail + self.num_new + self.num_err

    def counts(self) -> tuple[int, int, int, int]:
        return self.num_pass, self.num_fail, self.num_new, self.num_err

    def __str__(self) -> str:
        num_pass, num_fail, num_new, num_err = self.counts()
        summary = f'{num_pass} passed, {num_fail} failed, {num_new} created, {num_err} errors'
        sum_col = RED if num_fail or num_new or num_err else DIM
        return sum_col(summary)
