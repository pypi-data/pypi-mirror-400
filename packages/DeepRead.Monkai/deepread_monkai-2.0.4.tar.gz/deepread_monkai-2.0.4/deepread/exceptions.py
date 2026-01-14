# ============================================================================
# DEEPREAD - EXCEÇÕES
# ============================================================================
"""
Exceções customizadas do DeepRead.
"""


class DeepReadError(Exception):
    """Exceção base do DeepRead."""
    pass


class DocumentError(DeepReadError):
    """Erro relacionado ao documento."""
    pass


class ProcessingError(DeepReadError):
    """Erro durante o processamento."""
    pass


class ConfigurationError(DeepReadError):
    """Erro de configuração."""
    pass
