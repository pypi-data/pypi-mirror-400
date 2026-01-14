# ============================================================================
# DEEPREAD MODELS - CLASSIFICAÇÃO
# ============================================================================
"""
Modelos para classificação de documentos.
"""

from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field


class Classification(BaseModel):
    """
    Configuração de classificação.
    
    Attributes:
        system_prompt: Prompt de sistema para classificação
        user_prompt: Template do prompt (use {dados} como placeholder)
        response_model: Modelo Pydantic para a resposta
        
    Example:
        ```python
        from pydantic import BaseModel, Field
        from typing import Literal
        
        class ClassificacaoDoc(BaseModel):
            classificacao: Literal["APROVADO", "REPROVADO", "REVISAR"]
            justificativa: str
            confianca: float = Field(ge=0, le=1)
        
        classification = Classification(
            system_prompt="Você é um classificador de documentos.",
            user_prompt="Classifique baseado nos dados:\\n{dados}",
            response_model=ClassificacaoDoc
        )
        ```
    """
    system_prompt: str = Field(
        default="Você é um especialista em classificação de documentos.",
        description="Prompt de sistema"
    )
    user_prompt: str = Field(
        ...,
        description="Template do prompt. Use {dados} como placeholder."
    )
    response_model: Type[BaseModel] = Field(
        ...,
        description="Modelo Pydantic para structured output"
    )
    
    class Config:
        arbitrary_types_allowed = True


class ClassificationResult(BaseModel):
    """Resultado de uma classificação."""
    classification: str = ""
    justification: str = ""
    confidence: float = Field(default=0, ge=0, le=1)
    raw_result: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return self.model_dump()
