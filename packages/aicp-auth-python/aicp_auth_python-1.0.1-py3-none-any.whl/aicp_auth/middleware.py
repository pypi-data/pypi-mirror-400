"""
Middleware de autenticação para frameworks Python.
"""

from typing import Optional, Callable, Any, Dict, Union
from functools import wraps

from .client import KeycloakClient
from .types import AuthConfig, User, Permission, MiddlewareOptions
from .exceptions import AuthLibError, TokenVerificationError, PermissionDeniedError, RoleDeniedError


def _check_flask_installed():
    """Verifica se Flask está instalado."""
    try:
        import flask  # noqa: F401
        return True
    except ImportError:
        raise ImportError(
            "Flask não está instalado. "
            "Instale com: pip install aicp-auth-python[flask]"
        )


def _check_fastapi_installed():
    """Verifica se FastAPI está instalado."""
    try:
        import fastapi  # noqa: F401
        return True
    except ImportError:
        raise ImportError(
            "FastAPI não está instalado. "
            "Instale com: pip install aicp-auth-python[fastapi]"
        )


class AuthMiddleware:
    """
    Middleware genérico de autenticação.
    
    Pode ser usado como base para implementar middleware específicos
    para diferentes frameworks.
    """
    
    def __init__(self, config: AuthConfig, options: Optional[MiddlewareOptions] = None):
        """
        Inicializa o middleware.
        
        Args:
            config: Configuração de autenticação
            options: Opções do middleware
        """
        self.client = KeycloakClient(config)
        self.options = options or MiddlewareOptions()
    
    def authenticate(self, token: str) -> User:
        """
        Autentica um usuário através de um token.
        
        Args:
            token: Token JWT para autenticação
            
        Returns:
            Usuário autenticado
        """
        return self.client.authenticate(token)
    
    def check_permissions(self, user: User, permissions: list[Permission]) -> bool:
        """
        Verifica se um usuário tem todas as permissões necessárias.
        
        Args:
            user: Usuário para verificar
            permissions: Lista de permissões necessárias
            
        Returns:
            True se o usuário tem todas as permissões
        """
        return all(self.client.has_permission(user, perm) for perm in permissions)
    
    def check_roles(self, user: User, roles: list[str]) -> bool:
        """
        Verifica se um usuário tem pelo menos um dos roles necessários.
        
        Args:
            user: Usuário para verificar
            roles: Lista de roles necessários
            
        Returns:
            True se o usuário tem pelo menos um dos roles
        """
        return any(self.client.has_role(user, role) for role in roles)


def flask_auth_middleware(config: AuthConfig, options: Optional[MiddlewareOptions] = None):
    """
    Cria um decorator de autenticação para Flask.
    
    Args:
        config: Configuração de autenticação
        options: Opções do middleware
        
    Returns:
        Decorator para aplicar em rotas Flask
        
    Raises:
        ImportError: Se Flask não estiver instalado
    """
    _check_flask_installed()
    from flask import request, g, abort  # noqa: F401
    
    middleware = AuthMiddleware(config, options)
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extrai o token do header Authorization
            auth_header = request.headers.get(middleware.options.token_header, '')
            if not auth_header.startswith(middleware.options.token_prefix + ' '):
                if middleware.options.allow_anonymous:
                    return f(*args, **kwargs)
                abort(401, description="Token de autorização não fornecido")
            
            token = auth_header[len(middleware.options.token_prefix) + 1:]
            
            try:
                # Autentica o usuário
                user = middleware.authenticate(token)
                
                # Verifica roles se especificados
                if middleware.options.require_roles:
                    if not middleware.check_roles(user, middleware.options.require_roles):
                        abort(403, description="Role insuficiente")
                
                # Verifica permissões se especificadas
                if middleware.options.require_permissions:
                    if not middleware.check_permissions(user, middleware.options.require_permissions):
                        abort(403, description="Permissão insuficiente")
                
                # Adiciona o usuário ao contexto do Flask
                g.user = user
                
                return f(*args, **kwargs)
                
            except TokenVerificationError as e:
                if middleware.options.error_handler:
                    return middleware.options.error_handler(e)
                abort(401, description=str(e))
            except (PermissionDeniedError, RoleDeniedError) as e:
                if middleware.options.error_handler:
                    return middleware.options.error_handler(e)
                abort(403, description=str(e))
            except Exception as e:
                if middleware.options.error_handler:
                    return middleware.options.error_handler(e)
                abort(500, description="Erro interno do servidor")
        
        return decorated_function
    
    return decorator


def fastapi_auth_middleware(config: AuthConfig, options: Optional[MiddlewareOptions] = None):
    """
    Cria um dependency de autenticação para FastAPI.
    
    Args:
        config: Configuração de autenticação
        options: Opções do middleware
        
    Returns:
        Dependency para usar em rotas FastAPI
        
    Raises:
        ImportError: Se FastAPI não estiver instalado
    """
    _check_fastapi_installed()
    from fastapi import HTTPException, Depends, Request, status  # noqa: F401
    from fastapi import Request as FastAPIRequest
    
    middleware = AuthMiddleware(config, options)
    
    def get_current_user(request: FastAPIRequest) -> User:
        """
        Dependency para obter o usuário autenticado.
        
        Args:
            request: Request do FastAPI
            
        Returns:
            Usuário autenticado
            
        Raises:
            HTTPException: Se a autenticação falhar
        """
        # Extrai o token do header Authorization
        auth_header = request.headers.get(middleware.options.token_header, '')
        if not auth_header.startswith(middleware.options.token_prefix + ' '):
            if middleware.options.allow_anonymous:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de autorização não fornecido"
                )
        
        token = auth_header[len(middleware.options.token_prefix) + 1:]
        
        try:
            # Autentica o usuário
            user = middleware.authenticate(token)
            
            # Verifica roles se especificados
            if middleware.options.require_roles:
                if not middleware.check_roles(user, middleware.options.require_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Role insuficiente"
                    )
            
            # Verifica permissões se especificadas
            if middleware.options.require_permissions:
                if not middleware.check_permissions(user, middleware.options.require_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Permissão insuficiente"
                    )
            
            return user
            
        except TokenVerificationError as e:
            if middleware.options.error_handler:
                return middleware.options.error_handler(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except (PermissionDeniedError, RoleDeniedError) as e:
            if middleware.options.error_handler:
                return middleware.options.error_handler(e)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except Exception as e:
            if middleware.options.error_handler:
                return middleware.options.error_handler(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor"
            )
    
    return get_current_user


# Funções auxiliares para verificação de permissões e roles
def require_role(role: str):
    """
    Decorator para requerer um role específico.
    
    Args:
        role: Role necessário
        
    Returns:
        Decorator para aplicar em rotas Flask
        
    Raises:
        ImportError: Se Flask não estiver instalado
    """
    _check_flask_installed()
    from flask import g, abort  # noqa: F401
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Esta função deve ser usada em conjunto com o middleware de autenticação
            # que já adiciona o usuário ao contexto
            if hasattr(g, 'user'):
                user = g.user
                if not user or role not in user.roles:
                    abort(403, description=f"Role '{role}' necessário")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_permission(resource: str, action: str):
    """
    Decorator para requerer uma permissão específica.
    
    Args:
        resource: Recurso necessário
        action: Ação necessária
        
    Returns:
        Decorator para aplicar em rotas Flask
        
    Raises:
        ImportError: Se Flask não estiver instalado
    """
    _check_flask_installed()
    from flask import g, abort  # noqa: F401
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Esta função deve ser usada em conjunto com o middleware de autenticação
            if hasattr(g, 'user'):
                user = g.user
                if not user:
                    abort(403, description="Usuário não autenticado")
                
                permission = Permission(resource=resource, action=action)
                if not user.permissions or f"{resource}:{action}" not in user.permissions:
                    abort(403, description=f"Permissão '{resource}:{action}' necessária")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
