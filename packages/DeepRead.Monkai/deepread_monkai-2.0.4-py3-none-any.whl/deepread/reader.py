# ============================================================================
# DEEPREAD - CLASSE PRINCIPAL
# ============================================================================
"""
Classe principal do DeepRead para extração inteligente de documentos.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Type, Union

from pydantic import BaseModel
from openai import OpenAI as OpenAIClient

from .auth import validate_token, AuthToken
from .auth.exceptions import AuthenticationError, InvalidTokenError
from .config import DEFAULT_MODEL, MODELS, calculate_cost
from .models import Question, QuestionConfig, PageRange, Result, ProcessingResult, DocumentMetadata, Classification
from .models.result import ProcessingMetrics
from .utils import (
    load_pdf, 
    filter_relevant_pages, 
    get_document_metadata,
    extract_main_response,
)
from .ocr import process_pdf_smart
from .exceptions import DeepReadError, DocumentError, ProcessingError

logger = logging.getLogger(__name__)


class DeepRead:
    """
    DeepRead - Biblioteca para extração inteligente de documentos PDF.
    
    Attributes:
        api_token: Token de autenticação do DeepRead
        openai_api_key: Chave da API OpenAI
        model: Modelo a ser utilizado
        
    Example:
        ```python
        from deepread import DeepRead, Question, QuestionConfig
        from pydantic import BaseModel, Field
        
        # Definir modelo de resposta
        class ExtractionResponse(BaseModel):
            value: str = Field(description="Valor extraído")
            confidence: float = Field(default=1.0)
        
        # Criar pergunta
        question = Question(
            config=QuestionConfig(id="extraction", name="Extração"),
            system_prompt="Você é um especialista em extração.",
            user_prompt="Extraia informações de: {texto}",
            keywords=["valor", "total"],
            response_model=ExtractionResponse
        )
        
        # Inicializar DeepRead
        dr = DeepRead(
            api_token="dr_xxx...",
            openai_api_key="sk-..."
        )
        
        # Adicionar pergunta
        dr.add_question(question)
        
        # Processar documento
        result = dr.process("documento.pdf")
        print(result.get_answer("extraction"))
        ```
    """
    
    def __init__(
        self,
        api_token: str,
        openai_api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        validate_token_on_init: bool = True,
        auth_api_url: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Inicializa o DeepRead.
        
        Args:
            api_token: Token de autenticação do DeepRead
            openai_api_key: Chave da API OpenAI (ou usa OPENAI_API_KEY env)
            model: Modelo a ser utilizado
            validate_token_on_init: Se True, valida token na inicialização
            auth_api_url: URL da API de autenticação (opcional)
            verbose: Se True, imprime logs detalhados
            
        Raises:
            InvalidTokenError: Se o token for inválido
            AuthenticationError: Se houver erro de autenticação
        """
        self._api_token = api_token
        self._auth_token: Optional[AuthToken] = None
        self._auth_api_url = auth_api_url
        self._verbose = verbose
        
        # Validar token
        if validate_token_on_init:
            self._auth_token = self._validate_token()
        
        # Configurar OpenAI
        self._openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self._openai_api_key:
            raise DeepReadError("OpenAI API key não configurada. Defina OPENAI_API_KEY ou passe openai_api_key.")
        
        self._openai_client = OpenAIClient(api_key=self._openai_api_key)
        self._model = model
        
        # Perguntas e classificação
        self._questions: Dict[str, Question] = {}
        self._classification: Optional[Classification] = None
        
        if self._verbose:
            logger.info(f"DeepRead inicializado. Modelo: {model}")
    
    def _validate_token(self) -> AuthToken:
        """Valida o token de autenticação."""
        try:
            return validate_token(self._api_token)
        except (InvalidTokenError, AuthenticationError) as e:
            logger.error(f"Falha na autenticação: {e}")
            raise
    
    @property
    def user_id(self) -> Optional[str]:
        """Retorna o ID do usuário autenticado."""
        return self._auth_token.user_id if self._auth_token else None
    
    @property
    def model(self) -> str:
        """Retorna o modelo atual."""
        return self._model
    
    @model.setter
    def model(self, value: str):
        """Define o modelo a ser utilizado."""
        self._model = value
    
    @property
    def questions(self) -> List[Question]:
        """Retorna lista de perguntas configuradas."""
        return list(self._questions.values())
    
    # ========================================================================
    # CONFIGURAÇÃO DE PERGUNTAS
    # ========================================================================
    
    def add_question(self, question: Question) -> "DeepRead":
        """
        Adiciona uma pergunta para extração.
        
        Args:
            question: Question configurada
            
        Returns:
            self (para encadeamento)
        """
        self._questions[question.config.id] = question
        if self._verbose:
            logger.info(f"Pergunta adicionada: {question.config.id}")
        return self
    
    def add_questions(self, questions: List[Question]) -> "DeepRead":
        """
        Adiciona múltiplas perguntas.
        
        Args:
            questions: Lista de Questions
            
        Returns:
            self (para encadeamento)
        """
        for q in questions:
            self.add_question(q)
        return self
    
    def remove_question(self, question_id: str) -> "DeepRead":
        """Remove uma pergunta."""
        if question_id in self._questions:
            del self._questions[question_id]
        return self
    
    def clear_questions(self) -> "DeepRead":
        """Remove todas as perguntas."""
        self._questions.clear()
        return self
    
    def set_classification(self, classification: Classification) -> "DeepRead":
        """
        Configura classificação de documentos.
        
        Args:
            classification: Configuração de classificação
            
        Returns:
            self (para encadeamento)
        """
        self._classification = classification
        return self
    
    # ========================================================================
    # PROCESSAMENTO
    # ========================================================================
    
    def _execute_question(
        self,
        text: str,
        question: Question,
    ) -> Result:
        """Executa uma pergunta usando OpenAI."""
        start = time.time()
        
        try:
            user_prompt = question.user_prompt.format(texto=text)
            
            if question.response_model:
                # Structured output
                response = self._openai_client.beta.chat.completions.parse(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": question.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=question.response_model,
                )
                result = response.choices[0].message.parsed
                answer = extract_main_response(result)
                raw_result = result.model_dump() if hasattr(result, 'model_dump') else dict(result)
            else:
                # Resposta em texto
                response = self._openai_client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": question.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                answer = response.choices[0].message.content
                raw_result = {"response": answer}
            
            elapsed = time.time() - start
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            cost = calculate_cost(self._model, prompt_tokens, completion_tokens)
            
            return Result(
                question_id=question.config.id,
                question_name=question.config.name,
                answer=answer,
                raw_result=raw_result,
                metrics=ProcessingMetrics(
                    time_seconds=round(elapsed, 2),
                    tokens=total_tokens,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=round(cost, 6),
                    model=self._model,
                ),
                status="OK",
            )
            
        except Exception as e:
            logger.error(f"Erro ao executar pergunta {question.config.id}: {e}")
            return Result(
                question_id=question.config.id,
                question_name=question.config.name,
                answer=f"ERRO: {str(e)}",
                status="ERROR",
                metrics=ProcessingMetrics(time_seconds=time.time() - start),
            )
    
    def _classify_results(self, results: List[Result], doc_info: dict) -> Optional[Dict[str, Any]]:
        """Classifica os resultados extraídos."""
        if not self._classification:
            return None
        
        try:
            # Formatar dados para classificação
            data = {}
            for r in results:
                data[r.question_id] = r.answer
            data["_documento"] = doc_info.get("filename", "")
            data["_tipo"] = doc_info.get("doc_type", "")
            
            data_formatted = "\n".join([f"- {k}: {v}" for k, v in data.items()])
            prompt_final = self._classification.user_prompt.format(dados=data_formatted)
            
            response = self._openai_client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._classification.system_prompt},
                    {"role": "user", "content": prompt_final}
                ],
                response_format=self._classification.response_model,
            )
            
            result = response.choices[0].message.parsed
            return result.model_dump() if hasattr(result, 'model_dump') else dict(result)
            
        except Exception as e:
            logger.error(f"Erro na classificação: {e}")
            return {"error": str(e)}
    
    def process(
        self,
        document: Union[str, Path],
        questions: Optional[List[str]] = None,
        classify: bool = False,
    ) -> ProcessingResult:
        """
        Processa um documento PDF.
        
        Args:
            document: Caminho do documento PDF
            questions: Lista de IDs de perguntas específicas (None = todas)
            classify: Se True, classifica o documento após extração
            
        Returns:
            ProcessingResult com todos os resultados
            
        Raises:
            DocumentError: Se o documento não existir ou for inválido
        """
        pdf_path = Path(document)
        
        if not pdf_path.exists():
            raise DocumentError(f"Documento não encontrado: {document}")
        
        if self._verbose:
            logger.info(f"Processando: {pdf_path.name}")
        
        # Metadados
        metadata = get_document_metadata(pdf_path)
        doc_metadata = DocumentMetadata(
            filename=pdf_path.name,
            doc_type=metadata["doc_type"],
            num_pages=metadata["num_pages"],
            size_kb=metadata["size_kb"],
        )
        
        # Carregar documento (OCR automático se necessário)
        if metadata["doc_type"] == "image":
            if self._verbose:
                logger.info("Aplicando OCR...")
            documents = process_pdf_smart(pdf_path)
        else:
            documents = load_pdf(pdf_path)
        
        # Selecionar perguntas
        questions_to_run = []
        if questions:
            for qid in questions:
                if qid in self._questions:
                    questions_to_run.append(self._questions[qid])
        else:
            questions_to_run = list(self._questions.values())
        
        if not questions_to_run:
            raise ProcessingError("Nenhuma pergunta configurada. Use add_question() primeiro.")
        
        # Processar cada pergunta
        results: List[Result] = []
        total_time = 0
        total_tokens = 0
        total_cost = 0
        
        for question in questions_to_run:
            # 1. Aplicar filtro de range de páginas (se configurado)
            docs_to_process = documents
            page_range_applied = False
            page_range_ignored = False
            
            if question.page_range:
                total_pages = len(documents)
                page_indices, applied = question.page_range.get_page_indices(total_pages)
                
                if applied:
                    # Filtro foi aplicado
                    docs_to_process = [documents[i] for i in page_indices if i < len(documents)]
                    page_range_applied = True
                    if self._verbose:
                        logger.info(f"  {question.config.id}: Page range aplicado - páginas {page_indices[0]+1} a {page_indices[-1]+1}")
                else:
                    # Documento não tem páginas suficientes, filtro ignorado
                    page_range_ignored = True
                    if self._verbose:
                        logger.info(f"  {question.config.id}: Page range ignorado - documento tem apenas {total_pages} páginas")
            
            # 2. Aplicar filtro de keywords (sobre as páginas já filtradas por range)
            docs_filtered, info = filter_relevant_pages(docs_to_process, question.keywords)
            
            # Atualizar info com dados do page_range
            info["page_range_applied"] = page_range_applied
            info["page_range_ignored"] = page_range_ignored
            info["total"] = len(documents)  # Total original do documento
            
            if not docs_filtered:
                results.append(Result(
                    question_id=question.config.id,
                    question_name=question.config.name,
                    answer="Sem páginas relevantes",
                    status="NO_DATA",
                    pages_used=0,
                    pages_total=info["total"],
                ))
                continue
            
            # Juntar texto
            text = "\n\n---\n\n".join([doc.text for doc in docs_filtered])
            
            # Executar pergunta
            result = self._execute_question(text, question)
            result.pages_used = len(docs_filtered)
            result.pages_total = info["total"]
            results.append(result)
            
            total_time += result.metrics.time_seconds
            total_tokens += result.metrics.tokens
            total_cost += result.metrics.cost_usd
            
            if self._verbose:
                logger.info(f"  {question.config.id}: {result.answer[:50]}...")
        
        # Classificação
        classification = None
        if classify and self._classification:
            classification = self._classify_results(
                results, 
                {"filename": pdf_path.name, "doc_type": metadata["doc_type"]}
            )
        
        return ProcessingResult(
            document=doc_metadata,
            results=results,
            classification=classification,
            total_metrics=ProcessingMetrics(
                time_seconds=round(total_time, 2),
                tokens=total_tokens,
                cost_usd=round(total_cost, 6),
                model=self._model,
            ),
        )
    
    def process_batch(
        self,
        documents: List[Union[str, Path]],
        questions: Optional[List[str]] = None,
        classify: bool = False,
    ) -> List[ProcessingResult]:
        """
        Processa múltiplos documentos.
        
        Args:
            documents: Lista de caminhos de documentos
            questions: Lista de IDs de perguntas específicas
            classify: Se True, classifica os documentos
            
        Returns:
            Lista de ProcessingResult
        """
        results = []
        for doc in documents:
            try:
                result = self.process(doc, questions, classify)
                results.append(result)
            except (DocumentError, ProcessingError) as e:
                logger.error(f"Erro ao processar {doc}: {e}")
                # Adiciona resultado com erro
                results.append(ProcessingResult(
                    document=DocumentMetadata(filename=str(doc)),
                    results=[Result(
                        question_id="error",
                        answer=str(e),
                        status="ERROR",
                    )],
                ))
        return results
    
    # ========================================================================
    # UTILITÁRIOS
    # ========================================================================
    
    @staticmethod
    def available_models() -> Dict[str, str]:
        """Retorna modelos disponíveis."""
        return MODELS.copy()
    
    @staticmethod
    def create_question(
        question_id: str,
        name: str,
        user_prompt: str,
        system_prompt: str = "Você é um especialista em extração de informações.",
        keywords: List[str] = None,
        page_range: Optional[PageRange] = None,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Question:
        """
        Método de conveniência para criar uma Question.
        
        Args:
            question_id: ID único da pergunta
            name: Nome descritivo
            user_prompt: Template do prompt (use {texto} como placeholder)
            system_prompt: Prompt de sistema
            keywords: Keywords para filtrar páginas
            page_range: Range de páginas (PageRange ou None para todas)
            response_model: Modelo Pydantic para structured output
            
        Returns:
            Question configurada
            
        Examples:
            ```python
            from deepread import DeepRead, PageRange
            
            # Pergunta nas primeiras 5 páginas
            q1 = DeepRead.create_question(
                question_id="intro",
                name="Introdução",
                user_prompt="Extraia a introdução: {texto}",
                page_range=PageRange(start=1, end=5, from_position="start")
            )
            
            # Pergunta nas últimas 3 páginas
            q2 = DeepRead.create_question(
                question_id="conclusao",
                name="Conclusão",
                user_prompt="Extraia a conclusão: {texto}",
                page_range=PageRange(start=1, end=3, from_position="end")
            )
            ```
        """
        return Question(
            config=QuestionConfig(id=question_id, name=name),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            keywords=keywords or [],
            page_range=page_range,
            response_model=response_model,
        )
