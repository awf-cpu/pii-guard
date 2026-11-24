"""Check-digit validators. A match is only masked as CPF/CNPJ/CNJ if it validates,
which keeps false positives (order numbers, random digit runs) low."""
from __future__ import annotations

import re


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def valid_cpf(value: str) -> bool:
    d = _digits(value)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        total = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        if (total * 10 % 11) % 10 != int(d[n]):
            return False
    return True


def valid_cnpj(value: str) -> bool:
    d = _digits(value)
    if len(d) != 14 or d == d[0] * 14:
        return False

    def dv(base: str) -> int:
        weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        if len(base) == 13:
            weights = [6] + weights
        r = sum(int(c) * w for c, w in zip(base, weights)) % 11
        return 0 if r < 2 else 11 - r

    return dv(d[:12]) == int(d[12]) and dv(d[:13]) == int(d[13])


def valid_cnj(value: str) -> bool:
    """Unified court case number NNNNNNN-DD.AAAA.J.TR.OOOO (CNJ Res. 65/2008, mod 97)."""
    d = _digits(value)
    if len(d) != 20:
        return False
    n, dd, rest = d[:7], int(d[7:9]), d[9:]
    return 98 - (int(n + rest + "00") % 97) == dd
