# ============================================================================
# DEEPREAD AUTH - GESTÃO DE TOKENS
# ============================================================================
"""
Sistema de tokens de autenticação para o DeepRead.
Suporta validação local e via API externa.
"""

import hashlib
import hmac
import time
import base64
import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .exceptions import InvalidTokenError, ExpiredTokenError, AuthenticationError


# Chave secreta para assinatura (em produção, usar variável de ambiente)
SECRET_KEY = os.getenv("DEEPREAD_SECRET_KEY", "deepread_default_secret_key_change_in_production")


@dataclass
class AuthToken:
    """
    Token de autenticação do DeepRead.
    
    Attributes:
        token: String do token
        user_id: ID do usuário
        permissions: Permissões do usuário
        expires_at: Data de expiração
        metadata: Dados adicionais
    """
    token: str
    user_id: str
    permissions: list[str]
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @property
    def is_expired(self) -> bool:
        """Verifica se o token está expirado."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Verifica se o token é válido (não expirado)."""
        return not self.is_expired
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se o token tem uma permissão específica."""
        return permission in self.permissions or "*" in self.permissions
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "token": self.token,
            "user_id": self.user_id,
            "permissions": self.permissions,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }


def _create_signature(payload: str) -> str:
    """Cria assinatura HMAC para o payload."""
    return hmac.new(
        SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def generate_token(
    user_id: str,
    permissions: list[str] = None,
    expires_in_days: int = 30,
    metadata: Dict[str, Any] = None,
) -> AuthToken:
    """
    Gera um novo token de autenticação.
    
    Args:
        user_id: ID único do usuário
        permissions: Lista de permissões (default: ["read", "process"])
        expires_in_days: Dias até expiração (default: 30)
        metadata: Dados adicionais opcionais
        
    Returns:
        AuthToken com o token gerado
    """
    if permissions is None:
        permissions = ["read", "process"]
    
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # Criar payload
    payload = {
        "user_id": user_id,
        "permissions": permissions,
        "expires_at": expires_at.timestamp(),
        "created_at": datetime.utcnow().timestamp(),
        "metadata": metadata or {},
    }
    
    # Codificar payload
    payload_json = json.dumps(payload, sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
    
    # Criar assinatura
    signature = _create_signature(payload_b64)
    
    # Token final: payload.signature
    token = f"dr_{payload_b64}.{signature}"
    
    return AuthToken(
        token=token,
        user_id=user_id,
        permissions=permissions,
        expires_at=expires_at,
        metadata=metadata,
    )


def validate_token(token: str) -> AuthToken:
    """
    Valida um token e retorna os dados do usuário.
    
    Args:
        token: String do token (formato: dr_<payload>.<signature>)
        
    Returns:
        AuthToken se válido
        
    Raises:
        InvalidTokenError: Se o token for inválido
        ExpiredTokenError: Se o token estiver expirado
    """
    if not token:
        raise InvalidTokenError("Token não fornecido")
    
    # Verificar prefixo
    if not token.startswith("dr_"):
        raise InvalidTokenError("Token deve começar com 'dr_'")
    
    try:
        # Remover prefixo e separar payload/signature
        token_body = token[3:]  # Remove "dr_"
        
        if "." not in token_body:
            raise InvalidTokenError("Formato de token inválido")
        
        payload_b64, signature = token_body.rsplit(".", 1)
        
        # Verificar assinatura
        expected_signature = _create_signature(payload_b64)
        if not hmac.compare_digest(signature, expected_signature):
            raise InvalidTokenError("Assinatura do token inválida")
        
        # Decodificar payload
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        payload = json.loads(payload_json)
        
        # Verificar expiração
        expires_timestamp = payload.get("expires_at")
        expires_at = datetime.fromtimestamp(expires_timestamp) if expires_timestamp else None
        
        if expires_at and datetime.utcnow() > expires_at:
            raise ExpiredTokenError(f"Token expirou em {expires_at.isoformat()}")
        
        return AuthToken(
            token=token,
            user_id=payload["user_id"],
            permissions=payload.get("permissions", []),
            expires_at=expires_at,
            metadata=payload.get("metadata"),
        )
        
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise InvalidTokenError(f"Erro ao decodificar token: {str(e)}")


def validate_api_token(token: str, api_url: str = None) -> AuthToken:
    """
    Valida token via API externa (para integração com sistemas de autenticação).
    
    Args:
        token: Token a ser validado
        api_url: URL da API de validação
        
    Returns:
        AuthToken se válido
    """
    # Primeiro tenta validação local
    try:
        return validate_token(token)
    except (InvalidTokenError, ExpiredTokenError):
        pass
    
    # Se configurado, tenta validação via API
    if api_url:
        import requests
        
        try:
            response = requests.post(
                api_url,
                json={"token": token},
                timeout=5,
            )
            
            if response.status_code == 200:
                data = response.json()
                return AuthToken(
                    token=token,
                    user_id=data["user_id"],
                    permissions=data.get("permissions", ["read", "process"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                    metadata=data.get("metadata"),
                )
            else:
                raise InvalidTokenError(f"API retornou status {response.status_code}")
                
        except requests.RequestException as e:
            raise AuthenticationError(f"Erro ao validar token via API: {str(e)}")
    
    raise InvalidTokenError("Token inválido")
