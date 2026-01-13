"""
Exceções customizadas para a biblioteca de autenticação.
"""


class AuthLibError(Exception):
    """Exceção base para todas as exceções da biblioteca de autenticação."""
    pass


class TokenVerificationError(AuthLibError):
    """Erro durante a verificação de um token."""
    pass


class InvalidTokenError(TokenVerificationError):
    """Token inválido ou malformado."""
    pass


class TokenExpiredError(TokenVerificationError):
    """Token expirado."""
    pass


class InvalidAudienceError(TokenVerificationError):
    """Audience do token inválida."""
    pass


class InvalidIssuerError(TokenVerificationError):
    """Issuer do token inválido."""
    pass


class PermissionDeniedError(AuthLibError):
    """Usuário não tem permissão para acessar o recurso."""
    pass


class RoleDeniedError(AuthLibError):
    """Usuário não tem o role necessário."""
    pass


class ConfigurationError(AuthLibError):
    """Erro de configuração da biblioteca."""
    pass


class JWKSError(AuthLibError):
    """Erro ao acessar ou processar JWKS."""
    pass


class AuthenticationError(AuthLibError):
    """Erro de autenticação."""
    pass


class AuthorizationError(AuthLibError):
    """Erro de autorização."""
    pass
