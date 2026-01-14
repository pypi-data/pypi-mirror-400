# ============================================================================
# DEEPREAD AUTH - EXCEÇÕES DE AUTENTICAÇÃO
# ============================================================================
"""
Exceções relacionadas à autenticação.
"""


class AuthenticationError(Exception):
    """Erro base de autenticação."""
    
    def __init__(self, message: str = "Falha na autenticação"):
        self.message = message
        super().__init__(self.message)


class InvalidTokenError(AuthenticationError):
    """Token inválido ou mal formatado."""
    
    def __init__(self, message: str = "Token inválido"):
        super().__init__(message)


class ExpiredTokenError(AuthenticationError):
    """Token expirado."""
    
    def __init__(self, message: str = "Token expirado"):
        super().__init__(message)
