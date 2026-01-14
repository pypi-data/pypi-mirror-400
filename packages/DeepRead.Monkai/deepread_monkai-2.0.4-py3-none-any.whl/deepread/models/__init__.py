# ============================================================================
# DEEPREAD MODELS - MODELOS DE DADOS
# ============================================================================
"""
Modelos Pydantic para o DeepRead.
"""

from .question import Question, QuestionConfig, PageRange
from .result import Result, ProcessingResult, DocumentMetadata, ProcessingMetrics
from .classification import Classification, ClassificationResult

# Schemas de exemplo prontos para uso
from .schemas import (
    # Básicos
    TextoSimples,
    ValorMonetario,
    DataExtraida,
    ListaItens,
    # Documentos
    DadosContrato,
    DadosEdital,
    DadosProposta,
    DadosNotaFiscal,
    # Classificação
    ClassificacaoSimples,
    ClassificacaoBinaria,
    ClassificacaoTripartite,
    ClassificacaoRisco,
    ClassificacaoPrioridade,
    # Compostos
    AnaliseCompleta,
    ExtracacaoTabular,
)

__all__ = [
    # Core
    "Question",
    "QuestionConfig",
    "PageRange",
    "Result",
    "ProcessingResult",
    "DocumentMetadata",
    "ProcessingMetrics",
    "Classification",
    "ClassificationResult",
    # Schemas de exemplo - Básicos
    "TextoSimples",
    "ValorMonetario",
    "DataExtraida",
    "ListaItens",
    # Schemas de exemplo - Documentos
    "DadosContrato",
    "DadosEdital",
    "DadosProposta",
    "DadosNotaFiscal",
    # Schemas de exemplo - Classificação
    "ClassificacaoSimples",
    "ClassificacaoBinaria",
    "ClassificacaoTripartite",
    "ClassificacaoRisco",
    "ClassificacaoPrioridade",
    # Schemas de exemplo - Compostos
    "AnaliseCompleta",
    "ExtracacaoTabular",
]
