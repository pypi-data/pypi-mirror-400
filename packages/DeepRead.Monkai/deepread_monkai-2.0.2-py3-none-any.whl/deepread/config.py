# ============================================================================
# DEEPREAD CONFIG - CONFIGURAÇÕES
# ============================================================================
"""
Configurações do DeepRead.
"""

import os
from typing import Dict

# ============================================================================
# MODELOS DISPONÍVEIS
# ============================================================================
MODELS = {
    "fast": "gpt-4.1",
    "balanced": "gpt-5.1",
    "complete": "gpt-5-2025-08-07",
    "economic": "gpt-5-mini-2025-08-07",
}

DEFAULT_MODEL = MODELS["balanced"]

# ============================================================================
# PREÇOS POR 1M TOKENS
# ============================================================================
PRICING: Dict[str, Dict[str, float]] = {
    # GPT-5 Series
    "gpt-5.1": {"input": 1.25, "output": 10.00},
    "gpt-5": {"input": 1.25, "output": 10.00},
    "gpt-5-2025-08-07": {"input": 1.25, "output": 10.00},
    "gpt-5-mini": {"input": 0.25, "output": 2.00},
    "gpt-5-mini-2025-08-07": {"input": 0.25, "output": 2.00},
    # GPT-4.1 Series
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    # GPT-4o Series
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    # O-Series
    "o1": {"input": 15.00, "output": 60.00},
    "o3": {"input": 2.00, "output": 8.00},
    "o3-mini": {"input": 1.10, "output": 4.40},
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calcula custo em USD baseado nos tokens.
    
    Args:
        model: Nome do modelo
        prompt_tokens: Tokens do prompt
        completion_tokens: Tokens da resposta
        
    Returns:
        Custo em USD
    """
    if model not in PRICING:
        return 0.0
    pricing = PRICING[model]
    cost_input = (prompt_tokens / 1_000_000) * pricing["input"]
    cost_output = (completion_tokens / 1_000_000) * pricing["output"]
    return cost_input + cost_output


# ============================================================================
# CONFIGURAÇÃO DE OCR (AZURE)
# ============================================================================
def get_azure_config() -> tuple[str, str]:
    """Obtém configuração do Azure AI Vision."""
    endpoint = os.getenv("AZURE_AI_VISION_ENDPOINT", "")
    key = os.getenv("AZURE_AI_VISION_KEY", "")
    return endpoint, key


# ============================================================================
# CONFIGURAÇÃO DE VALIDAÇÃO
# ============================================================================
DEFAULT_MIN_CHARS_PER_PAGE = 100  # Mínimo de caracteres para considerar página com texto
