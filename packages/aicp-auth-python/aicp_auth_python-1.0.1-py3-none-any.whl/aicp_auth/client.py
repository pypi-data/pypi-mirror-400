"""
Cliente Keycloak para autenticação e autorização.
"""

import requests
import jwt
from jwt import PyJWKClient
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone

from .types import AuthConfig, User, Permission, TokenInfo
from .exceptions import (
    AuthLibError, TokenVerificationError, InvalidTokenError,
    TokenExpiredError, InvalidAudienceError, InvalidIssuerError,
    JWKSError, ConfigurationError
)


class KeycloakClient:
    """
    Cliente para integração com Keycloak.
    
    Fornece funcionalidades de verificação de tokens JWT, mapeamento de usuários
    e verificação de permissões e roles.
    """
    
    def __init__(self, config: AuthConfig):
        """
        Inicializa o cliente Keycloak.
        
        Args:
            config: Configuração de autenticação
        """
        self.config = config
        self._jwks_client: Optional[PyJWKClient] = None
        self._base_url = f"{config.url}/realms/{config.realm}"
        
        if not config.url or not config.realm or not config.client_id:
            raise ConfigurationError("URL, realm e client_id são obrigatórios")
    
    def _get_jwks_client(self) -> PyJWKClient:
        """Retorna o cliente JWKS para verificação de tokens."""
        if self._jwks_client is None:
            jwks_url = f"{self._base_url}/protocol/openid-connect/certs"
            self._jwks_client = PyJWKClient(jwks_url)
        return self._jwks_client
    
    def _get_signing_key(self, token: str) -> Any:
        """Obtém a chave de assinatura para um token específico."""
        try:
            jwks_client = self._get_jwks_client()
            return jwks_client.get_signing_key_from_jwt(token)
        except Exception as e:
            raise JWKSError(f"Erro ao obter chave de assinatura: {e}")
    
    def verify_token(self, token: str) -> TokenInfo:
        """
        Verifica e decodifica um token JWT.
        
        Args:
            token: Token JWT para verificar
            
        Returns:
            TokenInfo com as informações do token
            
        Raises:
            TokenVerificationError: Se o token for inválido
            TokenExpiredError: Se o token estiver expirado
            InvalidAudienceError: Se a audience for inválida
            InvalidIssuerError: Se o issuer for inválido
        """
        try:
            # Remove o prefixo "Bearer " se presente
            if token.startswith("Bearer "):
                token = token[7:]
            
            # Obtém a chave de assinatura
            signing_key = self._get_signing_key(token)
            
            # Opções de verificação
            verify_options = {
                'verify_signature': True,
                'verify_exp': True,
                'verify_iat': True,
                'verify_nbf': True,
                'algorithms': ['RS256']
            }
            
            # Verifica audience se configurado
            if self.config.verify_token_audience:
                if isinstance(self.config.verify_token_audience, str):
                    verify_options['audience'] = self.config.verify_token_audience
                else:
                    verify_options['audience'] = self.config.client_id
            
            # Verifica issuer se configurado
            if self.config.verify_token_issuer:
                verify_options['issuer'] = f"{self._base_url}"
            
            # Decodifica e verifica o token
            payload = jwt.decode(
                token,
                signing_key.key,
                options=verify_options
            )
            
            # Converte para TokenInfo
            token_info = TokenInfo(
                sub=payload.get('sub', ''),
                iss=payload.get('iss', ''),
                aud=payload.get('aud', ''),
                exp=payload.get('exp', 0),
                iat=payload.get('iat', 0),
                nbf=payload.get('nbf'),
                jti=payload.get('jti'),
                typ=payload.get('typ'),
                azp=payload.get('azp'),
                scope=payload.get('scope'),
                realm_access=payload.get('realm_access'),
                resource_access=payload.get('resource_access'),
                preferred_username=payload.get('preferred_username'),
                name=payload.get('name'),
                given_name=payload.get('given_name'),
                family_name=payload.get('family_name'),
                email=payload.get('email'),
                email_verified=payload.get('email_verified'),
                claims=payload
            )
            
            return token_info
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expirado")
        except jwt.InvalidAudienceError:
            raise InvalidAudienceError("Audience inválida")
        except jwt.InvalidIssuerError:
            raise InvalidIssuerError("Issuer inválido")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Token inválido: {e}")
        except Exception as e:
            raise TokenVerificationError(f"Erro ao verificar token: {e}")
    
    def map_token_to_user(self, token_info: TokenInfo) -> User:
        """
        Mapeia as informações do token para um objeto User.
        
        Args:
            token_info: Informações do token decodificado
            
        Returns:
            Objeto User mapeado
        """
        # Extrai roles do realm_access
        roles = []
        if token_info.realm_access and 'roles' in token_info.realm_access:
            roles.extend(token_info.realm_access['roles'])
        
        # Extrai permissões do scope
        permissions = []
        if token_info.scope:
            permissions = token_info.scope.split()
        
        # Extrai atributos adicionais
        attributes = {}
        for key, value in token_info.claims.items():
            if key not in ['sub', 'iss', 'aud', 'exp', 'iat', 'nbf', 'jti', 'typ', 'azp', 'scope', 'realm_access', 'resource_access']:
                attributes[key] = value
        
        return User(
            id=token_info.sub,
            username=token_info.preferred_username or token_info.sub,
            email=token_info.email,
            first_name=token_info.given_name,
            last_name=token_info.family_name,
            roles=roles,
            permissions=permissions,
            attributes=attributes,
            is_active=True,
            created_at=datetime.fromtimestamp(token_info.iat, tz=timezone.utc) if token_info.iat else None,
            updated_at=datetime.fromtimestamp(token_info.iat, tz=timezone.utc) if token_info.iat else None
        )
    
    def authenticate(self, token: str) -> User:
        """
        Autentica um usuário através de um token.
        
        Args:
            token: Token JWT para autenticação
            
        Returns:
            Objeto User autenticado
        """
        token_info = self.verify_token(token)
        return self.map_token_to_user(token_info)
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """
        Verifica se um usuário tem uma permissão específica.
        
        Args:
            user: Usuário para verificar
            permission: Permissão a ser verificada
            
        Returns:
            True se o usuário tem a permissão, False caso contrário
        """
        # Verifica permissões diretas
        permission_str = f"{permission.resource}:{permission.action}"
        if permission_str in user.permissions:
            return True
        
        # Verifica através de roles (implementação básica)
        # Em uma implementação real, você pode querer verificar permissões
        # específicas de cada role
        return False
    
    def has_role(self, user: User, role: str) -> bool:
        """
        Verifica se um usuário tem um role específico.
        
        Args:
            user: Usuário para verificar
            role: Role a ser verificado
            
        Returns:
            True se o usuário tem o role, False caso contrário
        """
        return role in user.roles
    
    def introspect_token(self, token: str) -> Dict[str, Any]:
        """
        Introspeciona um token através da API do Keycloak.
        
        Args:
            token: Token para introspecção
            
        Returns:
            Dicionário com informações do token
        """
        if not self.config.client_secret:
            raise ConfigurationError("client_secret é necessário para introspecção de token")
        
        url = f"{self._base_url}/protocol/openid-connect/token/introspect"
        data = {
            'token': token,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        try:
            response = requests.post(url, data=data, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise AuthLibError(f"Erro na introspecção do token: {e}")
    
    def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Obtém informações do usuário através da API do Keycloak.
        
        Args:
            token: Token de acesso
            
        Returns:
            Dicionário com informações do usuário
        """
        url = f"{self._base_url}/protocol/openid-connect/userinfo"
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise AuthLibError(f"Erro ao obter informações do usuário: {e}")
