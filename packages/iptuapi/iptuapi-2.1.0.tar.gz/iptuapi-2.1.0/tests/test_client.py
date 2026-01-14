"""
Tests for IPTUClient.
"""

import pytest
import responses
from responses import matchers

from iptuapi import (
    IPTUClient,
    ClientConfig,
    RetryConfig,
    CidadeEnum,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_create_client_with_api_key(self, api_key: str):
        """Test creating client with just API key."""
        client = IPTUClient(api_key)
        assert client.api_key == api_key
        assert client.config.base_url == "https://iptuapi.com.br/api/v1"

    def test_create_client_with_custom_config(self, api_key: str):
        """Test creating client with custom config."""
        config = ClientConfig(
            base_url="https://custom.api.com",
            timeout=60.0,
            log_requests=True,
        )
        client = IPTUClient(api_key, config=config)
        assert client.config.base_url == "https://custom.api.com"
        assert client.config.timeout == 60.0
        assert client.config.log_requests is True

    def test_create_client_with_shortcut_params(self, api_key: str):
        """Test creating client with shortcut parameters."""
        client = IPTUClient(api_key, base_url="https://test.api.com", timeout=45.0)
        assert client.config.base_url == "https://test.api.com"
        assert client.config.timeout == 45.0

    def test_create_client_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with pytest.raises(ValueError, match="API Key"):
            IPTUClient("")

    def test_client_context_manager(self, api_key: str):
        """Test client as context manager."""
        with IPTUClient(api_key) as client:
            assert client.api_key == api_key
        # Session should be closed after context

    def test_client_repr(self, api_key: str):
        """Test client string representation."""
        client = IPTUClient(api_key)
        assert "IPTUClient" in repr(client)
        assert "iptuapi.com.br" in repr(client)


class TestConsultaEndereco:
    """Tests for consulta_endereco endpoint."""

    @responses.activate
    def test_consulta_endereco_success(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test successful address query."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            headers={
                "X-RateLimit-Limit": "1000",
                "X-RateLimit-Remaining": "999",
                "X-RateLimit-Reset": "1704067200",
                "X-Request-ID": "req_123abc",
            },
        )

        result = client.consulta_endereco("Avenida Paulista", "1000")

        assert result["sql"] == "000.000.0000-0"
        assert result["logradouro"] == "Avenida Paulista"
        assert client.rate_limit is not None
        assert client.rate_limit.limit == 1000
        assert client.last_request_id == "req_123abc"

    @responses.activate
    def test_consulta_endereco_with_all_params(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test address query with all optional params."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            match=[
                matchers.query_param_matcher({
                    "logradouro": "Avenida Paulista",
                    "numero": "1000",
                    "complemento": "Sala 501",
                    "cidade": "sp",
                    "incluir_historico": "true",
                    "incluir_comparaveis": "true",
                    "incluir_zoneamento": "true",
                })
            ],
        )

        result = client.consulta_endereco(
            logradouro="Avenida Paulista",
            numero="1000",
            complemento="Sala 501",
            cidade=CidadeEnum.SAO_PAULO,
            incluir_historico=True,
            incluir_comparaveis=True,
            incluir_zoneamento=True,
        )

        assert result["logradouro"] == "Avenida Paulista"

    @responses.activate
    def test_consulta_endereco_not_found(self, client: IPTUClient, base_url: str):
        """Test 404 response raises NotFoundError."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json={"detail": "Imóvel não encontrado"},
            status=404,
        )

        with pytest.raises(NotFoundError) as exc_info:
            client.consulta_endereco("Rua Inexistente", "999")

        assert exc_info.value.status_code == 404


class TestConsultaSQL:
    """Tests for consulta_sql endpoint."""

    @responses.activate
    def test_consulta_sql_success(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test successful SQL query."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/sql/000.000.0000-0",
            json=sample_iptu_response,
            status=200,
        )

        result = client.consulta_sql("000.000.0000-0")

        assert result["sql"] == "000.000.0000-0"


class TestValuation:
    """Tests for valuation endpoints."""

    @responses.activate
    def test_valuation_estimate_success(
        self, client: IPTUClient, base_url: str, sample_valuation_response: dict
    ):
        """Test successful valuation estimate."""
        responses.add(
            responses.POST,
            f"{base_url}/valuation/estimate",
            json=sample_valuation_response,
            status=200,
        )

        result = client.valuation_estimate(
            area_terreno=500.0,
            area_construida=1200.0,
            bairro="Bela Vista",
            zona="ZC",
            tipo_uso="Comercial",
            tipo_padrao="Alto",
        )

        assert result["valor_estimado"] == 5000000.0
        assert result["confianca"] == 0.85

    @responses.activate
    def test_valuation_forbidden_for_basic_plan(
        self, client: IPTUClient, base_url: str
    ):
        """Test 403 response for basic plan."""
        responses.add(
            responses.POST,
            f"{base_url}/valuation/estimate",
            json={"detail": "Plano Pro ou superior necessário"},
            status=403,
        )

        with pytest.raises(ForbiddenError) as exc_info:
            client.valuation_estimate(
                area_terreno=500.0,
                area_construida=1200.0,
                bairro="Bela Vista",
                zona="ZC",
                tipo_uso="Comercial",
                tipo_padrao="Alto",
            )

        assert exc_info.value.status_code == 403


class TestErrorHandling:
    """Tests for error handling."""

    @responses.activate
    def test_authentication_error(self, client: IPTUClient, base_url: str):
        """Test 401 raises AuthenticationError."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json={"detail": "API Key inválida"},
            status=401,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            client.consulta_endereco("Avenida Paulista")

        assert exc_info.value.status_code == 401
        assert exc_info.value.is_retryable is False

    @responses.activate
    def test_validation_error(self, client: IPTUClient, base_url: str):
        """Test 400 raises ValidationError."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json={
                "detail": "Parâmetros inválidos",
                "errors": [
                    {"field": "logradouro", "message": "campo obrigatório"}
                ],
            },
            status=400,
        )

        with pytest.raises(ValidationError) as exc_info:
            client.consulta_endereco("")

        assert exc_info.value.status_code == 400
        assert len(exc_info.value.errors) == 1

    @responses.activate
    def test_rate_limit_error_with_retry_after(
        self, client: IPTUClient, base_url: str
    ):
        """Test 429 raises RateLimitError with retry_after."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json={"detail": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.consulta_endereco("Avenida Paulista")

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60
        assert exc_info.value.is_retryable is True

    @responses.activate
    def test_server_error(self, client: IPTUClient, base_url: str):
        """Test 500 raises ServerError."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json={"detail": "Internal server error"},
            status=500,
        )

        with pytest.raises(ServerError) as exc_info:
            client.consulta_endereco("Avenida Paulista")

        assert exc_info.value.status_code == 500
        assert exc_info.value.is_retryable is True


class TestRateLimitTracking:
    """Tests for rate limit tracking."""

    @responses.activate
    def test_rate_limit_extracted_from_headers(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test rate limit info is extracted from response headers."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            headers={
                "X-RateLimit-Limit": "5000",
                "X-RateLimit-Remaining": "4999",
                "X-RateLimit-Reset": "1704067200",
            },
        )

        assert client.rate_limit is None  # Before any request

        client.consulta_endereco("Avenida Paulista")

        assert client.rate_limit is not None
        assert client.rate_limit.limit == 5000
        assert client.rate_limit.remaining == 4999
        assert client.rate_limit.reset == 1704067200

    @responses.activate
    def test_rate_limit_none_when_headers_missing(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test rate limit is None when headers are missing."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
        )

        client.consulta_endereco("Avenida Paulista")

        assert client.rate_limit is None


class TestCidadeEnum:
    """Tests for cidade parameter handling."""

    @responses.activate
    def test_cidade_enum_sp(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test São Paulo enum value."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            match=[
                matchers.query_param_matcher({
                    "logradouro": "Avenida Paulista",
                    "cidade": "sp",
                }, strict_match=False)
            ],
        )

        client.consulta_endereco("Avenida Paulista", cidade=CidadeEnum.SAO_PAULO)

    @responses.activate
    def test_cidade_enum_bh(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test Belo Horizonte enum value."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            match=[
                matchers.query_param_matcher({
                    "logradouro": "Avenida Afonso Pena",
                    "cidade": "bh",
                }, strict_match=False)
            ],
        )

        client.consulta_endereco("Avenida Afonso Pena", cidade=CidadeEnum.BELO_HORIZONTE)

    @responses.activate
    def test_cidade_string_value(
        self, client: IPTUClient, base_url: str, sample_iptu_response: dict
    ):
        """Test string cidade value."""
        responses.add(
            responses.GET,
            f"{base_url}/consulta/endereco",
            json=sample_iptu_response,
            status=200,
            match=[
                matchers.query_param_matcher({
                    "logradouro": "Avenida Boa Viagem",
                    "cidade": "recife",
                }, strict_match=False)
            ],
        )

        client.consulta_endereco("Avenida Boa Viagem", cidade="recife")
