# ============================================================================
# DEEPREAD MODELS - RESULTADOS
# ============================================================================
"""
Modelos para resultados de processamento.
"""

from typing import Optional, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadados do documento processado."""
    filename: str = Field(..., description="Nome do arquivo")
    doc_type: str = Field(default="unknown", description="Tipo: texto ou imagem")
    num_pages: int = Field(default=0, description="Número de páginas")
    size_kb: float = Field(default=0, description="Tamanho em KB")
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class ProcessingMetrics(BaseModel):
    """Métricas de processamento."""
    time_seconds: float = Field(default=0, description="Tempo de processamento")
    tokens: int = Field(default=0, description="Total de tokens")
    prompt_tokens: int = Field(default=0, description="Tokens do prompt")
    completion_tokens: int = Field(default=0, description="Tokens da resposta")
    cost_usd: float = Field(default=0, description="Custo em USD")
    model: str = Field(default="", description="Modelo utilizado")


class Result(BaseModel):
    """
    Resultado de uma extração individual.
    
    Attributes:
        question_id: ID da pergunta
        question_name: Nome da pergunta
        answer: Resposta formatada
        raw_result: Resultado bruto do modelo
        metrics: Métricas de processamento
        status: Status (OK, ERRO, SEM_DADOS)
        pages_used: Páginas utilizadas
    """
    question_id: str
    question_name: str = ""
    answer: str = ""
    raw_result: Optional[Dict[str, Any]] = None
    metrics: ProcessingMetrics = Field(default_factory=ProcessingMetrics)
    status: str = "OK"
    pages_used: int = 0
    pages_total: int = 0
    
    def get_answer(self) -> str:
        """Retorna a resposta formatada."""
        return self.answer
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return self.model_dump()


class ProcessingResult(BaseModel):
    """
    Resultado completo do processamento de um documento.
    
    Attributes:
        document: Metadados do documento
        results: Lista de resultados por pergunta
        classification: Classificação (se aplicável)
        total_metrics: Métricas totais
    """
    document: DocumentMetadata
    results: List[Result] = Field(default_factory=list)
    classification: Optional[Dict[str, Any]] = None
    total_metrics: ProcessingMetrics = Field(default_factory=ProcessingMetrics)
    
    def get_result(self, question_id: str) -> Optional[Result]:
        """Obtém resultado de uma pergunta específica."""
        for r in self.results:
            if r.question_id == question_id:
                return r
        return None
    
    def get_answer(self, question_id: str) -> Optional[str]:
        """Obtém resposta de uma pergunta específica."""
        result = self.get_result(question_id)
        return result.answer if result else None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "document": self.document.model_dump(),
            "results": {r.question_id: r.to_dict() for r in self.results},
            "classification": self.classification,
            "total_metrics": self.total_metrics.model_dump(),
        }
    
    def to_flat_dict(self) -> dict:
        """Converte para dicionário plano (útil para CSV)."""
        flat = {
            "document": self.document.filename,
            "doc_type": self.document.doc_type,
            "num_pages": self.document.num_pages,
        }
        
        for r in self.results:
            flat[r.question_id] = r.answer
            
        if self.classification:
            flat["classification"] = self.classification.get("classification", "")
            
        flat["total_tokens"] = self.total_metrics.tokens
        flat["total_cost_usd"] = self.total_metrics.cost_usd
        
        return flat
