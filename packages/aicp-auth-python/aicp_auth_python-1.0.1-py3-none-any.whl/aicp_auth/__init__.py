"""
AICP Auth Library - Biblioteca de autenticação e autorização para Keycloak

Esta biblioteca fornece funcionalidades de autenticação e autorização para aplicações
Python, com suporte a Keycloak, JWT tokens e controle de acesso baseado em roles.

Uso on-premise:
    Para uso em soluções on-premise, esta biblioteca pode ser importada diretamente
    para lidar com instâncias Keycloak locais.
"""

from .client import KeycloakClient
from .types import AuthConfig, User, Permission, TokenInfo, AuthContext, MiddlewareOptions
from .exceptions import (
    AuthLibError, TokenVerificationError, InvalidTokenError,
    TokenExpiredError, InvalidAudienceError, InvalidIssuerError,
    PermissionDeniedError, RoleDeniedError, ConfigurationError, JWKSError
)
from .middleware import AuthMiddleware

# Middlewares opcionais - serão importados apenas quando solicitados
# Para usar, importe diretamente: from aicp_auth.middleware import flask_auth_middleware
# Ou instale as dependências: pip install aicp-auth-python[flask] ou [fastapi]

def __getattr__(name):
    """
    Importação lazy de middlewares opcionais.
    
    Permite importar flask_auth_middleware ou fastapi_auth_middleware
    sem quebrar o import se as dependências não estiverem instaladas.
    """
    if name == "flask_auth_middleware":
        try:
            from .middleware import flask_auth_middleware
            return flask_auth_middleware
        except ImportError as e:
            raise ImportError(
                f"Não foi possível importar {name}. "
                "Flask não está instalado. "
                "Instale com: pip install aicp-auth-python[flask]"
            ) from e
    elif name == "fastapi_auth_middleware":
        try:
            from .middleware import fastapi_auth_middleware
            return fastapi_auth_middleware
        except ImportError as e:
            raise ImportError(
                f"Não foi possível importar {name}. "
                "FastAPI não está instalado. "
                "Instale com: pip install aicp-auth-python[fastapi]"
            ) from e
    raise AttributeError(f"módulo 'aicp_auth' não tem atributo '{name}'")

__version__ = "1.0.1"
__author__ = "AI Cockpit Team"
__email__ = "team@ai-cockpit.com"

__all__ = [
    # Classes principais
    "KeycloakClient",
    "AuthMiddleware",
    
    # Tipos
    "AuthConfig",
    "User", 
    "Permission",
    "TokenInfo",
    "AuthContext",
    "MiddlewareOptions",
    
    # Exceções
    "AuthLibError",
    "TokenVerificationError",
    "InvalidTokenError",
    "TokenExpiredError",
    "InvalidAudienceError",
    "InvalidIssuerError",
    "PermissionDeniedError",
    "RoleDeniedError",
    "ConfigurationError",
    "JWKSError",
    
    # Funções de middleware (opcionais - requerem dependências extras)
    # Use: from aicp_auth import flask_auth_middleware
    # Ou: pip install aicp-auth-python[flask]
    "flask_auth_middleware",
    "fastapi_auth_middleware",
]
