# pii-guard

[![CI](https://github.com/awf-cpu/pii-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/awf-cpu/pii-guard/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

Mask **Brazilian personal data** before text is sent to an LLM, and restore it afterwards if you want. Zero dependencies, fully offline.

## The business problem

Sending customer text to a third-party model is a data-protection decision (LGPD). Most masking libraries target US formats. Brazilian text is full of CPF, CNPJ, court case numbers, phones with area codes and CEPs, and naive regexes either miss them or mangle ordinary numbers.

## How it works

- **Validated, not guessed.** CPF, CNPJ and CNJ case numbers (mod-97) are masked only if their check digits are valid, so `pedido 123.456.789-00` is left alone.
- **Specific before generic.** A CNJ number contains digit runs that look like phones; rules run in an order that prevents that.
- **Stable tokens.** The same value always becomes the same placeholder (`[CPF_1]`), so the model can still reason about "the same person" without seeing the data.
- **Reversible, locally.** `unmask(answer, mapping)` restores originals; the mapping never leaves your machine.

```python
from pii_guard import mask, unmask

m = mask("Cliente 529.982.247-25, fone (48) 99999-1234, ana@example.com")
print(m.text)    # Cliente [CPF_1], fone [PHONE_1], [EMAIL_1]
answer = call_your_llm(m.text)
print(unmask(answer, m.mapping))
```

CLI: `echo "..." | python -m pii_guard`

## Scope and honesty

Detects structured identifiers only. It does **not** detect free-form names or addresses; pair it with an NER step if you need those. Treat it as one layer of a privacy design, not a guarantee.

## Develop

```bash
pip install pytest && pytest -q
```

MIT licensed. Built by André Feix · [LinkedIn](https://www.linkedin.com/in/andrefeix)
