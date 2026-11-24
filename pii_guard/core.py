from __future__ import annotations

import re
from dataclasses import dataclass, field

from .validators import valid_cnj, valid_cnpj, valid_cpf

# Order matters: longer / more specific patterns first so they are not
# swallowed by looser ones (a CNJ number contains digit runs that look like phones).
_RULES = [
    ("CNJ", re.compile(r"(?<!\d)\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}(?!\d)"), valid_cnj),
    ("CNPJ", re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)"), valid_cnpj),
    ("CPF", re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)"), valid_cpf),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), None),
    ("PHONE", re.compile(r"(?<![\d])(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}-?\d{4}(?!\d)"), None),
    ("CEP", re.compile(r"(?<!\d)\d{5}-\d{3}(?!\d)"), None),
]


@dataclass
class Masked:
    text: str
    mapping: dict[str, str] = field(default_factory=dict)  # token -> original
    counts: dict[str, int] = field(default_factory=dict)


def mask(text: str, kinds: set[str] | None = None) -> Masked:
    """Replace PII with stable placeholders like ``[CPF_1]``.

    The same value always maps to the same token, so the LLM can still reason
    about "the same person" without seeing the data. ``kinds`` restricts masking.
    """
    mapping: dict[str, str] = {}
    reverse: dict[tuple[str, str], str] = {}
    counts: dict[str, int] = {}

    for kind, pattern, check in _RULES:
        if kinds and kind not in kinds:
            continue

        def repl(m: re.Match, kind=kind, check=check) -> str:
            raw = m.group(0)
            if check and not check(raw):
                return raw
            key = (kind, re.sub(r"\W", "", raw).lower())
            if key not in reverse:
                counts[kind] = counts.get(kind, 0) + 1
                token = f"[{kind}_{counts[kind]}]"
                reverse[key] = token
                mapping[token] = raw
            return reverse[key]

        text = pattern.sub(repl, text)
    return Masked(text=text, mapping=mapping, counts=counts)


def unmask(text: str, mapping: dict[str, str]) -> str:
    """Restore originals in an LLM answer (optional, keep the mapping local)."""
    for token, original in mapping.items():
        text = text.replace(token, original)
    return text
