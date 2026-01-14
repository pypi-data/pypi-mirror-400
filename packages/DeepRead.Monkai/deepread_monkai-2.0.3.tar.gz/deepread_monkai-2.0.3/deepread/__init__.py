# ============================================================================
# DEEPREAD - BIBLIOTECA DE EXTRAÇÃO INTELIGENTE DE DOCUMENTOS
# ============================================================================
"""
DeepRead - Biblioteca para extração e classificação inteligente de documentos PDF.

Uso básico:
    from deepread import DeepRead
    
    # Inicializar com token de autenticação
    dr = DeepRead(api_token="seu_token_aqui")
    
    # Processar documento
    resultado = dr.process("documento.pdf")
"""

__version__ = "2.0.3"
__author__ = "Monkai"

from .reader import DeepRead
from .auth import AuthToken, AuthenticationError, InvalidTokenError
from .models import (
    # Core models
    Question, 
    QuestionConfig,
    PageRange,
    Result, 
    ProcessingResult,
    DocumentMetadata,
    ProcessingMetrics,
    Classification,
    # Example schemas
    DadosContrato,
    DadosEdital,
    ClassificacaoTripartite,
)
from .exceptions import DeepReadError, DocumentError, ProcessingError

__all__ = [
    # Main class
    "DeepRead",
    # Auth
    "AuthToken",
    "AuthenticationError", 
    "InvalidTokenError",
    # Core Models
    "Question",
    "QuestionConfig",
    "PageRange",
    "Result",
    "ProcessingResult",
    "DocumentMetadata",
    "ProcessingMetrics",
    "Classification",
    # Example Schemas
    "DadosContrato",
    "DadosEdital",
    "ClassificacaoTripartite",
    # Exceptions
    "DeepReadError",
    "DocumentError",
    "ProcessingError",
]
