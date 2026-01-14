"""LostArkAPI 클라이언트 테스트."""

import pytest
from unittest.mock import Mock, patch
from pyloa.client import LostArkAPI
from pyloa.rate_limiter import RateLimiter


def test_client_initialization():
    """클라이언트가 API 키로 초기화되어야 합니다."""
    api = LostArkAPI(api_key="test_jwt_token")

    assert api.api_key == "test_jwt_token"
    assert api.base_url == "https://developer-lostark.game.onstove.com"


def test_client_creates_session_with_headers():
    """클라이언트가 적절한 헤더로 세션을 생성해야 합니다."""
    api = LostArkAPI(api_key="test_jwt_token")

    assert api.session is not None
    assert "authorization" in api.session.headers
    assert api.session.headers["authorization"] == "bearer test_jwt_token"
    assert api.session.headers["accept"] == "application/json"


def test_client_initializes_rate_limiter():
    """클라이언트가 RateLimiter 인스턴스를 생성해야 합니다."""
    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.rate_limiter, RateLimiter)
    assert api.rate_limiter.limit == 100
    assert api.rate_limiter.remaining == 100


def test_api_key_is_required():
    """클라이언트는 API 키가 필요해야 합니다."""
    with pytest.raises(TypeError):
        LostArkAPI()


def test_api_key_immutable():
    """API 키는 초기화 후 수정할 수 없어야 합니다."""
    api = LostArkAPI(api_key="test_jwt_token")

    # Should raise AttributeError when trying to set
    with pytest.raises(AttributeError):
        api.api_key = "new_key"


def test_client_provides_news_endpoint():
    """클라이언트가 NewsEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.news import NewsEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.news, NewsEndpoint)
    # Should return same instance (lazy initialization)
    assert api.news is api.news


def test_client_provides_characters_endpoint():
    """클라이언트가 CharactersEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.characters import CharactersEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.characters, CharactersEndpoint)
    # Should return same instance (lazy initialization)
    assert api.characters is api.characters


def test_client_provides_markets_endpoint():
    """클라이언트가 MarketsEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.markets import MarketsEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.markets, MarketsEndpoint)
    # Should return same instance (lazy initialization)
    assert api.markets is api.markets


def test_client_provides_auctions_endpoint():
    """클라이언트가 AuctionsEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.auctions import AuctionsEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.auctions, AuctionsEndpoint)
    # Should return same instance (lazy initialization)
    assert api.auctions is api.auctions


def test_client_provides_game_contents_endpoint():
    """클라이언트가 GameContentsEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.game_contents import GameContentsEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.game_contents, GameContentsEndpoint)
    # Should return same instance (lazy initialization)
    assert api.game_contents is api.game_contents


def test_client_provides_armories_endpoint():
    """클라이언트가 ArmoriesEndpoint에 접근할 수 있어야 합니다."""
    from pyloa.endpoints.armories import ArmoriesEndpoint

    api = LostArkAPI(api_key="test_jwt_token")

    assert isinstance(api.armories, ArmoriesEndpoint)
    # Should return same instance (lazy initialization)
    assert api.armories is api.armories
