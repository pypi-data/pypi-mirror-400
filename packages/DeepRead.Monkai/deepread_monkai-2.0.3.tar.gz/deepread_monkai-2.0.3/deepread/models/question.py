# ============================================================================
# DEEPREAD MODELS - PERGUNTAS
# ============================================================================
"""
Modelos para definição de perguntas/extrações.
"""

from typing import Optional, Type, List, Any, Literal, Union, Tuple
from pydantic import BaseModel, Field, model_validator


class PageRange(BaseModel):
    """
    Configuração de range de páginas para filtrar.
    
    Attributes:
        start: Página inicial (1-indexed)
        end: Página final (1-indexed, ou None para até o final)
        from_position: De onde contar: "start" (início) ou "end" (final)
        
    Examples:
        - PageRange(start=1, end=5, from_position="start")  # Páginas 1-5 do início
        - PageRange(start=1, end=5, from_position="end")    # Últimas 5 páginas
        - PageRange(start=1, end=3, from_position="start")  # Primeiras 3 páginas
        - PageRange(start=1, end=10, from_position="end")   # Últimas 10 páginas
    """
    start: int = Field(default=1, ge=1, description="Página inicial (1-indexed)")
    end: Optional[int] = Field(default=None, ge=1, description="Página final (None = até o fim)")
    from_position: Literal["start", "end"] = Field(
        default="start",
        description="De onde contar: 'start' (início do documento) ou 'end' (final do documento)"
    )
    
    def get_page_indices(self, total_pages: int) -> Tuple[List[int], bool]:
        """
        Calcula os índices das páginas a serem usadas.
        
        Args:
            total_pages: Total de páginas do documento
            
        Returns:
            Tuple: (lista de índices 0-indexed, se o filtro foi aplicado)
            Se o documento não tiver páginas suficientes, retorna todas as páginas
            e False indicando que o filtro foi ignorado.
        """
        end_page = self.end or total_pages
        
        if self.from_position == "start":
            # Páginas do início: 1-5 = índices 0-4
            start_idx = self.start - 1
            end_idx = min(end_page, total_pages)
            
            # Se o range excede o documento, usar todas as páginas
            if start_idx >= total_pages:
                return list(range(total_pages)), False
            
            # Se o range cobre todas as páginas ou mais, considerar como "não aplicado"
            # (o filtro não está realmente restringindo nada)
            if start_idx == 0 and end_idx >= total_pages:
                return list(range(total_pages)), False
            
            return list(range(start_idx, end_idx)), True
            
        else:  # from_position == "end"
            # Páginas do final: últimas N páginas
            # Se end=5, pegar as últimas 5 páginas
            num_pages_to_get = end_page - self.start + 1
            
            # Se o documento não tem páginas suficientes, usar todas
            if num_pages_to_get >= total_pages:
                return list(range(total_pages)), False
            
            start_idx = total_pages - num_pages_to_get
            return list(range(start_idx, total_pages)), True


class QuestionConfig(BaseModel):
    """
    Configuração de uma pergunta/extração.
    
    Attributes:
        id: Identificador único da pergunta
        name: Nome descritivo
        description: Descrição da pergunta
        tag: Tag para identificação no resultado
        type: Tipo de resposta esperada
    """
    id: str = Field(..., description="Identificador único")
    name: str = Field(..., description="Nome descritivo")
    description: str = Field(default="", description="Descrição da pergunta")
    tag: str = Field(default="", description="Tag para o resultado")
    type: str = Field(default="string", description="Tipo de resposta")
    
    class Config:
        extra = "allow"


class Question(BaseModel):
    """
    Definição completa de uma pergunta/extração.
    
    Attributes:
        config: Configuração básica da pergunta
        system_prompt: Prompt de sistema para o LLM
        user_prompt: Template do prompt do usuário (use {texto} como placeholder)
        keywords: Keywords para filtrar páginas relevantes
        page_range: Range de páginas para filtrar (opcional)
        response_model: Modelo Pydantic para a resposta (opcional)
    
    Example:
        ```python
        from pydantic import BaseModel, Field
        from deepread.models import PageRange
        
        class QuantidadeResponse(BaseModel):
            quantidade: float = Field(description="Quantidade em litros")
            unidade: str = Field(default="L")
        
        # Exemplo 1: Usar apenas as primeiras 5 páginas
        question = Question(
            config=QuestionConfig(id="intro", name="Introdução"),
            user_prompt="Extraia informações da introdução:\\n\\n{texto}",
            page_range=PageRange(start=1, end=5, from_position="start"),
        )
        
        # Exemplo 2: Usar apenas as últimas 3 páginas
        question = Question(
            config=QuestionConfig(id="conclusao", name="Conclusão"),
            user_prompt="Extraia a conclusão:\\n\\n{texto}",
            page_range=PageRange(start=1, end=3, from_position="end"),
        )
        
        # Exemplo 3: Combinar page_range com keywords
        question = Question(
            config=QuestionConfig(id="valor", name="Valor"),
            user_prompt="Extraia o valor:\\n\\n{texto}",
            page_range=PageRange(start=1, end=10, from_position="start"),
            keywords=["valor", "preço", "R$"],
        )
        ```
    """
    config: QuestionConfig
    system_prompt: str = Field(
        default="Você é um especialista em extração de informações de documentos.",
        description="Prompt de sistema"
    )
    user_prompt: str = Field(
        ..., 
        description="Template do prompt do usuário. Use {texto} como placeholder para o conteúdo do documento."
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords para filtrar páginas relevantes"
    )
    page_range: Optional[PageRange] = Field(
        default=None,
        description="Range de páginas para filtrar. Se o documento não tiver páginas suficientes, o filtro é ignorado."
    )
    response_model: Optional[Type[BaseModel]] = Field(
        default=None,
        description="Modelo Pydantic para structured output"
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """
        Cria uma Question a partir de um dicionário.
        
        Args:
            data: Dicionário com os campos da pergunta
            
        Returns:
            Question configurada
        """
        config_data = data.get("config", {})
        if not config_data.get("id"):
            config_data["id"] = data.get("id", "unknown")
        if not config_data.get("name"):
            config_data["name"] = data.get("name", config_data["id"])
        
        # Parse page_range if present
        page_range = None
        if data.get("page_range"):
            pr_data = data["page_range"]
            if isinstance(pr_data, dict):
                page_range = PageRange(**pr_data)
            elif isinstance(pr_data, PageRange):
                page_range = pr_data
            
        return cls(
            config=QuestionConfig(**config_data),
            system_prompt=data.get("system_prompt", ""),
            user_prompt=data.get("user_prompt", ""),
            keywords=data.get("keywords", []),
            page_range=page_range,
            response_model=data.get("response_model"),
        )
    
    def to_dict(self) -> dict:
        """Converte para dicionário (sem response_model)."""
        result = {
            "config": self.config.model_dump(),
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "keywords": self.keywords,
        }
        if self.page_range:
            result["page_range"] = self.page_range.model_dump()
        return result
