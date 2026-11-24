"""pii-guard: mask Brazilian personal data before text reaches an LLM."""
from .core import Masked, mask, unmask
from .validators import valid_cnj, valid_cnpj, valid_cpf

__all__ = ["mask", "unmask", "Masked", "valid_cpf", "valid_cnpj", "valid_cnj"]
__version__ = "0.1.0"
