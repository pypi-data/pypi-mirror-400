"""
Tests for exceptions module.
"""

import pytest

from iptuapi import (
    IPTUAPIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    TimeoutError,
    NetworkError,
    QuotaExceededError,
    raise_for_status,
)


class TestIPTUAPIError:
    """Tests for base IPTUAPIError."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = IPTUAPIError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.status_code is None
        assert error.request_id is None

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = IPTUAPIError("Error", status_code=500)
        assert "[HTTP 500]" in str(error)
        assert error.status_code == 500

    def test_error_with_request_id(self):
        """Test error with request ID."""
        error = IPTUAPIError("Error", request_id="req_abc123")
        assert "[Request ID: req_abc123]" in str(error)
        assert error.request_id == "req_abc123"

    def test_error_repr(self):
        """Test error representation."""
        error = IPTUAPIError("Error", status_code=500, request_id="req_123")
        repr_str = repr(error)
        assert "IPTUAPIError" in repr_str
        assert "Error" in repr_str
        assert "500" in repr_str

    def test_is_retryable_for_500_errors(self):
        """Test is_retryable property."""
        assert IPTUAPIError("Error", status_code=500).is_retryable is True
        assert IPTUAPIError("Error", status_code=502).is_retryable is True
        assert IPTUAPIError("Error", status_code=503).is_retryable is True
        assert IPTUAPIError("Error", status_code=504).is_retryable is True
        assert IPTUAPIError("Error", status_code=429).is_retryable is True

    def test_is_not_retryable_for_client_errors(self):
        """Test is_retryable is False for client errors."""
        assert IPTUAPIError("Error", status_code=400).is_retryable is False
        assert IPTUAPIError("Error", status_code=401).is_retryable is False
        assert IPTUAPIError("Error", status_code=403).is_retryable is False
        assert IPTUAPIError("Error", status_code=404).is_retryable is False


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert "API Key" in str(error)
        assert error.status_code == 401

    def test_custom_message(self):
        """Test custom error message."""
        error = AuthenticationError("Token expirado")
        assert str(error) == "Token expirado [HTTP 401]"

    def test_is_not_retryable(self):
        """Test auth errors are not retryable."""
        assert AuthenticationError().is_retryable is False


class TestForbiddenError:
    """Tests for ForbiddenError."""

    def test_default_message(self):
        """Test default error message."""
        error = ForbiddenError()
        assert "Acesso negado" in str(error)
        assert error.status_code == 403

    def test_with_required_plan(self):
        """Test error with required plan."""
        error = ForbiddenError(required_plan="Pro")
        assert "Pro" in str(error)
        assert error.required_plan == "Pro"


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_default_message(self):
        """Test default error message."""
        error = RateLimitError()
        assert "Limite de requisições" in str(error)
        assert error.status_code == 429

    def test_with_retry_after(self):
        """Test error with retry_after."""
        error = RateLimitError(retry_after=60)
        assert "60 segundos" in str(error)
        assert error.retry_after == 60

    def test_with_limit_info(self):
        """Test error with limit info."""
        error = RateLimitError(limit=1000, remaining=0)
        assert error.limit == 1000
        assert error.remaining == 0

    def test_is_always_retryable(self):
        """Test rate limit errors are always retryable."""
        assert RateLimitError().is_retryable is True


class TestValidationError:
    """Tests for ValidationError."""

    def test_default_message(self):
        """Test default error message."""
        error = ValidationError()
        assert "Parâmetros inválidos" in str(error)
        assert error.status_code == 400

    def test_with_errors_list(self):
        """Test error with validation errors list."""
        errors = [
            {"field": "logradouro", "message": "campo obrigatório"},
            {"field": "cidade", "message": "valor inválido"},
        ]
        error = ValidationError(errors=errors)
        assert "logradouro" in str(error)
        assert "cidade" in str(error)
        assert len(error.errors) == 2


class TestServerError:
    """Tests for ServerError."""

    def test_default_message(self):
        """Test default error message."""
        error = ServerError()
        assert "Erro interno" in str(error)
        assert error.status_code == 500

    def test_custom_status_code(self):
        """Test with custom status code."""
        error = ServerError(status_code=503)
        assert error.status_code == 503

    def test_is_always_retryable(self):
        """Test server errors are always retryable."""
        assert ServerError().is_retryable is True


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_default_message(self):
        """Test default error message."""
        error = TimeoutError()
        assert "Timeout" in str(error)

    def test_with_timeout_seconds(self):
        """Test error with timeout seconds."""
        error = TimeoutError(timeout_seconds=30.0)
        assert "30" in str(error)
        assert error.timeout_seconds == 30.0

    def test_is_retryable(self):
        """Test timeout errors are retryable."""
        assert TimeoutError().is_retryable is True


class TestNetworkError:
    """Tests for NetworkError."""

    def test_default_message(self):
        """Test default error message."""
        error = NetworkError()
        assert "conexão" in str(error)

    def test_with_original_error(self):
        """Test error with original exception."""
        original = ConnectionError("Connection refused")
        error = NetworkError(original_error=original)
        assert "Connection refused" in str(error)
        assert error.original_error is original

    def test_is_retryable(self):
        """Test network errors are retryable."""
        assert NetworkError().is_retryable is True


class TestQuotaExceededError:
    """Tests for QuotaExceededError."""

    def test_default_message(self):
        """Test default error message."""
        error = QuotaExceededError()
        assert "Cota mensal" in str(error)
        assert error.status_code == 403

    def test_with_usage_info(self):
        """Test error with usage info."""
        error = QuotaExceededError(
            monthly_limit=10000,
            current_usage=10000,
            reset_date="2024-02-01",
        )
        assert "10000/10000" in str(error)
        assert error.monthly_limit == 10000
        assert error.current_usage == 10000
        assert error.reset_date == "2024-02-01"


class TestRaiseForStatus:
    """Tests for raise_for_status function."""

    def test_success_does_not_raise(self):
        """Test 2xx status codes don't raise."""
        raise_for_status(200)
        raise_for_status(201)
        raise_for_status(204)

    def test_400_raises_validation_error(self):
        """Test 400 raises ValidationError."""
        with pytest.raises(ValidationError):
            raise_for_status(400)

    def test_401_raises_authentication_error(self):
        """Test 401 raises AuthenticationError."""
        with pytest.raises(AuthenticationError):
            raise_for_status(401)

    def test_403_raises_forbidden_error(self):
        """Test 403 raises ForbiddenError."""
        with pytest.raises(ForbiddenError):
            raise_for_status(403)

    def test_404_raises_not_found_error(self):
        """Test 404 raises NotFoundError."""
        with pytest.raises(NotFoundError):
            raise_for_status(404)

    def test_422_raises_validation_error(self):
        """Test 422 raises ValidationError."""
        with pytest.raises(ValidationError):
            raise_for_status(422)

    def test_429_raises_rate_limit_error(self):
        """Test 429 raises RateLimitError."""
        with pytest.raises(RateLimitError):
            raise_for_status(429)

    def test_500_raises_server_error(self):
        """Test 500 raises ServerError."""
        with pytest.raises(ServerError):
            raise_for_status(500)

    def test_unknown_status_raises_base_error(self):
        """Test unknown status raises IPTUAPIError."""
        with pytest.raises(IPTUAPIError):
            raise_for_status(418)

    def test_with_response_body(self):
        """Test error includes response body detail."""
        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(400, response_body={"detail": "Campo inválido"})
        assert "Campo inválido" in str(exc_info.value)

    def test_with_request_id(self):
        """Test error includes request ID."""
        with pytest.raises(ServerError) as exc_info:
            raise_for_status(500, request_id="req_test123")
        assert exc_info.value.request_id == "req_test123"

    def test_429_with_retry_after(self):
        """Test 429 includes retry_after."""
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(429, retry_after=120)
        assert exc_info.value.retry_after == 120

    def test_validation_error_with_errors_list(self):
        """Test validation error extracts errors list."""
        errors = [{"field": "email", "message": "formato inválido"}]
        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(400, response_body={"errors": errors})
        assert exc_info.value.errors == errors
