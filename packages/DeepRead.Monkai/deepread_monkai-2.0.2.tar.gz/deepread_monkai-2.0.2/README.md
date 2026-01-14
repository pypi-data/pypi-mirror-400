# 📚 DeepRead

**Biblioteca Python para extração inteligente de documentos PDF com IA**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Características

- 🔐 **Autenticação por Token** - Sistema seguro de autenticação
- 📄 **Extração Inteligente** - Extrai informações de PDFs usando LLMs
- 🔍 **OCR Automático** - Detecta e processa documentos baseados em imagem
- 📊 **Structured Output** - Respostas tipadas com Pydantic
- ⚡ **Modular** - Configure perguntas e classificações dinamicamente
- 💰 **Tracking de Custos** - Monitore tokens e custos por requisição

---

## 🚀 Instalação

```bash
pip install deepread
```

Ou instale do source:

```bash
git clone https://github.com/BeMonkAI/deepread.git
cd deepread
pip install -e .
```

Para suporte a OCR (Azure):

```bash
pip install deepread[ocr]
```

---

## 📖 Uso Rápido

### 1. Gerar Token de Autenticação

```python
from deepread.auth import generate_token

# Gerar token para um usuário
token = generate_token(
    user_id="user_123",
    permissions=["read", "process"],
    expires_in_days=30
)

print(f"Token: {token.token}")
# dr_eyJ1c2VyX2lkIjog...
```

### 2. Configurar e Processar Documentos

```python
from deepread import DeepRead, Question, QuestionConfig
from pydantic import BaseModel, Field

# Definir modelo de resposta estruturada
class ExtractionResponse(BaseModel):
    valor: str = Field(description="Valor extraído")
    unidade: str = Field(default="", description="Unidade de medida")
    confianca: float = Field(default=1.0, ge=0, le=1)

# Criar pergunta
question = Question(
    config=QuestionConfig(
        id="quantidade",
        name="Extração de Quantidade",
        description="Extrai quantidade do documento"
    ),
    system_prompt="Você é um especialista em extração de dados de documentos.",
    user_prompt="""
    Analise o texto e extraia a quantidade mencionada.
    
    Texto:
    {texto}
    """,
    keywords=["quantidade", "litros", "volume", "total"],
    response_model=ExtractionResponse
)

# Inicializar DeepRead
dr = DeepRead(
    api_token="dr_seu_token_aqui",
    openai_api_key="sk-sua_key_aqui",  # ou use OPENAI_API_KEY env
    model="gpt-5.1",  # opcional
    verbose=True
)

# Adicionar pergunta
dr.add_question(question)

# Processar documento
result = dr.process("documento.pdf")

# Acessar resultados
print(f"Resposta: {result.get_answer('quantidade')}")
print(f"Tokens: {result.total_metrics.tokens}")
print(f"Custo: ${result.total_metrics.cost_usd:.4f}")
```

### 3. Múltiplas Perguntas

```python
# Adicionar várias perguntas de uma vez
dr.add_questions([
    Question(
        config=QuestionConfig(id="preco", name="Preço"),
        user_prompt="Extraia o preço: {texto}",
        keywords=["preço", "valor", "R$"]
    ),
    Question(
        config=QuestionConfig(id="data", name="Data"),
        user_prompt="Extraia a data: {texto}",
        keywords=["data", "prazo", "vigência"]
    ),
])

# Processar todas as perguntas
result = dr.process("documento.pdf")

# Acessar cada resposta
for r in result.results:
    print(f"{r.question_name}: {r.answer}")
```

### 4. Classificação de Documentos

```python
from deepread import Classification
from typing import Literal

class ClassificacaoDoc(BaseModel):
    classificacao: Literal["APROVADO", "REPROVADO", "REVISAR"]
    justificativa: str
    confianca: float = Field(ge=0, le=1)

# Configurar classificação
classification = Classification(
    system_prompt="Você é um classificador de documentos.",
    user_prompt="""
    Baseado nos dados extraídos, classifique o documento:
    
    {dados}
    """,
    response_model=ClassificacaoDoc
)

dr.set_classification(classification)

# Processar com classificação
result = dr.process("documento.pdf", classify=True)
print(f"Classificação: {result.classification}")
```

### 5. Processamento em Lote

```python
from pathlib import Path

# Listar documentos
docs = list(Path("documentos/").glob("*.pdf"))

# Processar todos
results = dr.process_batch(docs, classify=True)

# Exportar para CSV
import csv

with open("resultados.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].to_flat_dict().keys())
    writer.writeheader()
    for r in results:
        writer.writerow(r.to_flat_dict())
```

---

## 🔐 Sistema de Autenticação

O DeepRead usa tokens JWT-like para autenticação:

```python
from deepread.auth import generate_token, validate_token

# Gerar token
token = generate_token(
    user_id="user_123",
    permissions=["read", "process", "classify"],
    expires_in_days=30,
    metadata={"company": "Acme Corp"}
)

# Validar token
try:
    auth = validate_token(token.token)
    print(f"Usuário: {auth.user_id}")
    print(f"Permissões: {auth.permissions}")
except InvalidTokenError:
    print("Token inválido!")
except ExpiredTokenError:
    print("Token expirado!")
```

### Variáveis de Ambiente

Configure a chave secreta para produção:

```bash
export DEEPREAD_SECRET_KEY="sua_chave_secreta_muito_segura"
export OPENAI_API_KEY="sk-..."
export AZURE_AI_VISION_KEY="..."  # Para OCR
export AZURE_AI_VISION_ENDPOINT="https://..."
```

---

## 📊 Modelos Disponíveis

```python
from deepread import DeepRead

# Listar modelos
print(DeepRead.available_models())
# {
#     "fast": "gpt-4.1",
#     "balanced": "gpt-5.1",
#     "complete": "gpt-5-2025-08-07",
#     "economic": "gpt-5-mini-2025-08-07"
# }
```

---

## 🛠️ API Reference

### `DeepRead`

| Método | Descrição |
|--------|-----------|
| `add_question(question)` | Adiciona uma pergunta |
| `add_questions(questions)` | Adiciona múltiplas perguntas |
| `remove_question(id)` | Remove uma pergunta |
| `set_classification(config)` | Configura classificação |
| `process(document)` | Processa um documento |
| `process_batch(documents)` | Processa múltiplos documentos |

### `Question`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `config` | `QuestionConfig` | Configuração básica |
| `system_prompt` | `str` | Prompt de sistema |
| `user_prompt` | `str` | Template do prompt (use `{texto}`) |
| `keywords` | `list[str]` | Keywords para filtrar páginas |
| `response_model` | `BaseModel` | Modelo Pydantic (opcional) |

### `ProcessingResult`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `document` | `DocumentMetadata` | Metadados do documento |
| `results` | `list[Result]` | Resultados por pergunta |
| `classification` | `dict` | Classificação (se aplicável) |
| `total_metrics` | `ProcessingMetrics` | Métricas totais |

---

## 📁 Estrutura do Projeto

```
deepread/
├── __init__.py          # Exports principais
├── reader.py            # Classe DeepRead
├── config.py            # Configurações
├── utils.py             # Utilitários
├── ocr.py               # Módulo OCR
├── exceptions.py        # Exceções
├── auth/
│   ├── __init__.py
│   ├── token.py         # Gestão de tokens
│   └── exceptions.py    # Exceções de auth
└── models/
    ├── __init__.py
    ├── question.py      # Modelo Question
    ├── result.py        # Modelos de resultado
    └── classification.py # Modelo Classification
```

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido por [Monkai](https://www.monkai.com.br)** 🐵
