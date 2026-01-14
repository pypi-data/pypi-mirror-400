# ============================================================================
# DEEPREAD AUTH - MÓDULO DE AUTENTICAÇÃO
# ============================================================================
"""
Sistema de autenticação por token para o DeepRead.

⚠️  IMPORTANTE: Os tokens de acesso são fornecidos EXCLUSIVAMENTE pela equipe Monkai.
Para solicitar seu token, entre em contato: contato@monkai.com.br

A geração de tokens é uma função INTERNA usada pela equipe Monkai para 
controle de segurança e gestão de acessos à biblioteca. Usuários devem
apenas utilizar a função validate_token para verificar seus tokens.
"""

from .token import AuthToken, validate_token
from .exceptions import AuthenticationError, InvalidTokenError, ExpiredTokenError

# _generate_token é uma função INTERNA usada apenas pela equipe Monkai
# para controle de segurança e acesso à biblioteca - NÃO EXPORTADA
from .token import _generate_token as _generate_token  # noqa: F401

__all__ = [
    "AuthToken",
    "validate_token",
    "AuthenticationError",
    "InvalidTokenError",
    "ExpiredTokenError",
]
