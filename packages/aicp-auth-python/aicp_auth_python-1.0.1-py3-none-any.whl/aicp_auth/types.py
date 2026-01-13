"""
Tipos e estruturas de dados para a biblioteca de autenticação.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


@dataclass
class AuthConfig:
    """Configuração de autenticação para Keycloak."""
    url: str
    realm: str
    client_id: str
    client_secret: Optional[str] = None
    public_key: Optional[str] = None
    verify_token_audience: Union[bool, str] = True
    verify_token_issuer: bool = True
    timeout: int = 30


@dataclass
class User:
    """Representa um usuário autenticado."""
    id: str
    username: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Permission:
    """Representa uma permissão específica."""
    resource: str
    action: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class TokenInfo:
    """Informações extraídas de um JWT token."""
    sub: str
    iss: str
    aud: Union[str, List[str]]
    exp: int
    iat: int
    nbf: Optional[int] = None
    jti: Optional[str] = None
    typ: Optional[str] = None
    azp: Optional[str] = None
    scope: Optional[str] = None
    realm_access: Optional[Dict[str, Any]] = None
    resource_access: Optional[Dict[str, Any]] = None
    preferred_username: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    claims: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthContext:
    """Contexto de autenticação para permissões."""
    user_id: str
    organization_id: Optional[str] = None
    project_id: Optional[str] = None
    environment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MiddlewareOptions:
    """Opções de configuração para o middleware."""
    require_auth: bool = True
    require_roles: Optional[List[str]] = None
    require_permissions: Optional[List[Permission]] = None
    allow_anonymous: bool = False
    error_handler: Optional[callable] = None
    user_property: str = "user"
    token_header: str = "Authorization"
    token_prefix: str = "Bearer"
