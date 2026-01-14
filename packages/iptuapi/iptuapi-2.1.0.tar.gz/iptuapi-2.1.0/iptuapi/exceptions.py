"""
Exceções do SDK IPTU API.

Hierarquia de exceções para tratamento granular de erros.
"""

from __future__ import annotations

from typing import Any, Optional


class IPTUAPIError(Exception):
    """
    Exceção base para erros da IPTU API.

    Attributes:
        message: Mensagem de erro
        status_code: Código HTTP da resposta
        response_body: Corpo da resposta de erro
        request_id: ID da requisição para suporte
        retry_after: Segundos para retry (se aplicável)
    """

    def __init__(
        self,
        message: str = "Erro na API IPTU",
        status_code: Optional[int] = None,
        response_body: Optional[dict[str, Any]] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response_body = response_body or {}
        self.request_id = request_id
        self.retry_after = retry_after
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"[HTTP {self.status_code}]")
        if self.request_id:
            parts.append(f"[Request ID: {self.request_id}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )

    @property
    def is_retryable(self) -> bool:
        """Indica se o erro pode ser recuperável via retry."""
        return self.status_code in (429, 500, 502, 503, 504)


class AuthenticationError(IPTUAPIError):
    """Erro de autenticação (HTTP 401)."""

    def __init__(
        self,
        message: str = "API Key inválida ou não fornecida",
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, status_code=401, **kwargs)


class ForbiddenError(IPTUAPIError):
    """Erro de autorização (HTTP 403)."""

    def __init__(
        self,
        message: str = "Acesso negado. Verifique se seu plano permite este recurso.",
        required_plan: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.required_plan = required_plan
        if required_plan:
            message = f"{message} Plano necessário: {required_plan}"
        super().__init__(message=message, status_code=403, **kwargs)


class NotFoundError(IPTUAPIError):
    """Recurso não encontrado (HTTP 404)."""

    def __init__(
        self,
        message: str = "Imóvel ou recurso não encontrado",
        **kwargs: Any,
    ) -> None:
        super().__init__(message=message, status_code=404, **kwargs)


class RateLimitError(IPTUAPIError):
    """Limite de requisições excedido (HTTP 429)."""

    def __init__(
        self,
        message: str = "Limite de requisições excedido",
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: int = 0,
        **kwargs: Any,
    ) -> None:
        self.limit = limit
        self.remaining = remaining
        if retry_after:
            message = f"{message}. Tente novamente em {retry_after} segundos."
        super().__init__(message=message, status_code=429, retry_after=retry_after, **kwargs)

    @property
    def is_retryable(self) -> bool:
        return True


class ValidationError(IPTUAPIError):
    """Erro de validação (HTTP 400/422)."""

    def __init__(
        self,
        message: str = "Parâmetros inválidos",
        errors: Optional[list[dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        self.errors = errors or []
        if errors:
            error_details = "; ".join(
                f"{e.get('field', 'unknown')}: {e.get('message', e.get('msg', 'erro'))}"
                for e in errors
            )
            message = f"{message}: {error_details}"
        super().__init__(message=message, status_code=400, **kwargs)


class ServerError(IPTUAPIError):
    """Erro interno do servidor (HTTP 5xx)."""

    def __init__(
        self,
        message: str = "Erro interno do servidor",
        **kwargs: Any,
    ) -> None:
        status_code = kwargs.pop("status_code", 500)
        super().__init__(message=message, status_code=status_code, **kwargs)

    @property
    def is_retryable(self) -> bool:
        return True


class TimeoutError(IPTUAPIError):
    """Timeout na requisição."""

    def __init__(
        self,
        message: str = "Timeout na requisição",
        timeout_seconds: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            message = f"{message} (limite: {timeout_seconds}s)"
        super().__init__(message=message, **kwargs)

    @property
    def is_retryable(self) -> bool:
        return True


class NetworkError(IPTUAPIError):
    """Erro de rede/conexão."""

    def __init__(
        self,
        message: str = "Erro de conexão com a API",
        original_error: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        self.original_error = original_error
        if original_error:
            message = f"{message}: {str(original_error)}"
        super().__init__(message=message, **kwargs)

    @property
    def is_retryable(self) -> bool:
        return True


class QuotaExceededError(IPTUAPIError):
    """Cota mensal excedida."""

    def __init__(
        self,
        message: str = "Cota mensal de requisições excedida",
        reset_date: Optional[str] = None,
        current_usage: Optional[int] = None,
        monthly_limit: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self.reset_date = reset_date
        self.current_usage = current_usage
        self.monthly_limit = monthly_limit
        if monthly_limit:
            message = f"{message}. Uso: {current_usage or '?'}/{monthly_limit}"
        super().__init__(message=message, status_code=403, **kwargs)


# Mapeamento de status code para exceção
STATUS_CODE_EXCEPTIONS: dict[int, type[IPTUAPIError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: ServerError,
}


def raise_for_status(
    status_code: int,
    response_body: Optional[dict[str, Any]] = None,
    request_id: Optional[str] = None,
    retry_after: Optional[int] = None,
) -> None:
    """Levanta a exceção apropriada baseada no status code."""
    if 200 <= status_code < 300:
        return

    response_body = response_body or {}
    detail = response_body.get("detail", "")

    # Handle detail being a dict (e.g., {"success": false, "error": "...", "detail": "..."})
    if isinstance(detail, dict):
        message = detail.get("error") or detail.get("detail") or detail.get("message") or str(detail)
    else:
        message = str(detail) if detail else ""

    exception_class = STATUS_CODE_EXCEPTIONS.get(status_code, IPTUAPIError)

    kwargs: dict[str, Any] = {
        "response_body": response_body,
        "request_id": request_id,
    }

    if status_code == 429:
        kwargs["retry_after"] = retry_after

    if status_code in (400, 422) and "errors" in response_body:
        kwargs["errors"] = response_body["errors"]

    if message:
        kwargs["message"] = message

    raise exception_class(**kwargs)
