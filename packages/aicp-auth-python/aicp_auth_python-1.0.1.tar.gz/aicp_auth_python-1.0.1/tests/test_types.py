"""
Testes para tipos da biblioteca.
"""
import pytest
from aicp_auth.types import AuthConfig, User, Permission, TokenInfo
from datetime import datetime, timezone


def test_auth_config():
    """Testa criação de AuthConfig."""
    config = AuthConfig(
        url="https://keycloak.example.com",
        realm="test-realm",
        client_id="test-client"
    )
    
    assert config.url == "https://keycloak.example.com"
    assert config.realm == "test-realm"
    assert config.client_id == "test-client"


def test_user():
    """Testa criação de User."""
    user = User(
        id="user-123",
        username="testuser",
        email="test@example.com",
        roles=["user", "admin"]
    )
    
    assert user.id == "user-123"
    assert "user" in user.roles


def test_permission():
    """Testa criação de Permission."""
    permission = Permission(
        resource="api",
        action="read"
    )
    
    assert permission.resource == "api"
    assert permission.action == "read"


def test_token_info():
    """Testa criação de TokenInfo."""
    token_info = TokenInfo(
        sub="user-123",
        iss="https://keycloak.example.com/realms/test",
        aud="test-client",
        exp=9999999999,
        iat=1000000000
    )
    
    assert token_info.sub == "user-123"
    assert token_info.aud == "test-client"

