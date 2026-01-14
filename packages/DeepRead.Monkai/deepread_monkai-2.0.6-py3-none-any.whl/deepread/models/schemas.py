# ============================================================================
# DEEPREAD MODELS - SCHEMAS DE EXEMPLO
# ============================================================================
"""
Schemas de exemplo prontos para uso.
Importe e use diretamente ou como base para criar seus próprios.

Uso:
    from deepread.models.schemas import (
        TextoSimples,
        ValorMonetario,
        DadosContrato,
        ClassificacaoSimples,
    )
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# SCHEMAS BÁSICOS
# ============================================================================

class TextoSimples(BaseModel):
    """Resposta em texto simples."""
    texto: str = Field(description="Texto extraído")
    confianca: float = Field(default=1.0, ge=0, le=1, description="Confiança na extração")


class ValorMonetario(BaseModel):
    """Valor monetário extraído."""
    valor: float = Field(description="Valor numérico")
    moeda: str = Field(default="BRL", description="Código da moeda")
    formatado: str = Field(default="", description="Valor formatado como string")
    
    def get_main_response(self) -> str:
        return f"{self.moeda} {self.valor:,.2f}"


class DataExtraida(BaseModel):
    """Data extraída do documento."""
    data: str = Field(description="Data no formato DD/MM/AAAA")
    tipo: str = Field(default="", description="Tipo da data (assinatura, vigência, etc)")


class ListaItens(BaseModel):
    """Lista de itens extraídos."""
    itens: List[str] = Field(description="Lista de itens encontrados")
    total: int = Field(default=0, description="Total de itens")


# ============================================================================
# SCHEMAS DE DOCUMENTOS
# ============================================================================

class DadosContrato(BaseModel):
    """Dados extraídos de um contrato."""
    numero_contrato: str = Field(default="", description="Número do contrato")
    valor_total: float = Field(default=0, description="Valor total em reais")
    prazo_vigencia: str = Field(default="", description="Prazo de vigência")
    data_assinatura: Optional[str] = Field(default=None, description="Data de assinatura")
    partes: List[str] = Field(default_factory=list, description="Partes envolvidas")
    objeto: str = Field(default="", description="Objeto do contrato")
    
    def get_main_response(self) -> str:
        return f"Contrato {self.numero_contrato}: R$ {self.valor_total:,.2f}"


class DadosEdital(BaseModel):
    """Dados extraídos de um edital de licitação."""
    numero_edital: str = Field(description="Número do edital")
    orgao: str = Field(default="", description="Órgão licitante")
    modalidade: str = Field(default="", description="Modalidade (pregão, concorrência, etc)")
    objeto: str = Field(default="", description="Objeto da licitação")
    valor_estimado: float = Field(default=0, description="Valor estimado")
    data_abertura: Optional[str] = Field(default=None, description="Data de abertura")
    requisitos: List[str] = Field(default_factory=list, description="Requisitos de habilitação")


class DadosProposta(BaseModel):
    """Dados extraídos de uma proposta comercial."""
    empresa: str = Field(description="Nome da empresa")
    cnpj: str = Field(default="", description="CNPJ")
    valor_proposta: float = Field(default=0, description="Valor da proposta")
    prazo_entrega: str = Field(default="", description="Prazo de entrega")
    validade_proposta: str = Field(default="", description="Validade da proposta")
    condicoes_pagamento: str = Field(default="", description="Condições de pagamento")


class DadosNotaFiscal(BaseModel):
    """Dados extraídos de uma nota fiscal."""
    numero_nf: str = Field(description="Número da nota fiscal")
    data_emissao: str = Field(default="", description="Data de emissão")
    valor_total: float = Field(default=0, description="Valor total")
    cnpj_emitente: str = Field(default="", description="CNPJ do emitente")
    cnpj_destinatario: str = Field(default="", description="CNPJ do destinatário")
    itens: List[str] = Field(default_factory=list, description="Itens da nota")


# ============================================================================
# SCHEMAS DE CLASSIFICAÇÃO
# ============================================================================

class ClassificacaoSimples(BaseModel):
    """Classificação simples de documento."""
    classificacao: str = Field(description="Classificação do documento")
    justificativa: str = Field(description="Justificativa para a classificação")
    confianca: float = Field(ge=0, le=1, description="Nível de confiança")


class ClassificacaoBinaria(BaseModel):
    """Classificação binária (sim/não)."""
    aprovado: bool = Field(description="Se o documento foi aprovado")
    motivo: str = Field(description="Motivo da decisão")
    pontos_positivos: List[str] = Field(default_factory=list)
    pontos_negativos: List[str] = Field(default_factory=list)


class ClassificacaoTripartite(BaseModel):
    """Classificação em três categorias."""
    classificacao: Literal["APROVADO", "REPROVADO", "REVISAR"] = Field(
        description="Classificação final"
    )
    justificativa: str = Field(description="Justificativa detalhada")
    confianca: float = Field(ge=0, le=1, description="Confiança na classificação")
    recomendacoes: List[str] = Field(default_factory=list, description="Recomendações")


class ClassificacaoRisco(BaseModel):
    """Classificação de risco."""
    nivel_risco: Literal["baixo", "medio", "alto", "critico"] = Field(
        description="Nível de risco"
    )
    score: float = Field(ge=0, le=100, description="Score de risco (0-100)")
    fatores_risco: List[str] = Field(default_factory=list, description="Fatores de risco")
    mitigacoes: List[str] = Field(default_factory=list, description="Ações de mitigação")


class ClassificacaoPrioridade(BaseModel):
    """Classificação de prioridade."""
    prioridade: Literal["urgente", "alta", "media", "baixa"] = Field(
        description="Nível de prioridade"
    )
    prazo_sugerido: str = Field(default="", description="Prazo sugerido")
    responsavel_sugerido: str = Field(default="", description="Responsável sugerido")
    justificativa: str = Field(description="Justificativa da priorização")


# ============================================================================
# SCHEMAS COMPOSTOS
# ============================================================================

class AnaliseCompleta(BaseModel):
    """Análise completa de documento."""
    resumo: str = Field(description="Resumo executivo")
    pontos_principais: List[str] = Field(description="Pontos principais")
    valores_encontrados: List[float] = Field(default_factory=list)
    datas_relevantes: List[str] = Field(default_factory=list)
    entidades_mencionadas: List[str] = Field(default_factory=list)
    classificacao: str = Field(default="", description="Classificação sugerida")


class ExtracacaoTabular(BaseModel):
    """Extração de dados tabulares."""
    cabecalhos: List[str] = Field(description="Cabeçalhos das colunas")
    linhas: List[List[str]] = Field(description="Linhas de dados")
    total_linhas: int = Field(default=0, description="Total de linhas encontradas")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Básicos
    "TextoSimples",
    "ValorMonetario",
    "DataExtraida",
    "ListaItens",
    # Documentos
    "DadosContrato",
    "DadosEdital",
    "DadosProposta",
    "DadosNotaFiscal",
    # Classificação
    "ClassificacaoSimples",
    "ClassificacaoBinaria",
    "ClassificacaoTripartite",
    "ClassificacaoRisco",
    "ClassificacaoPrioridade",
    # Compostos
    "AnaliseCompleta",
    "ExtracacaoTabular",
]
