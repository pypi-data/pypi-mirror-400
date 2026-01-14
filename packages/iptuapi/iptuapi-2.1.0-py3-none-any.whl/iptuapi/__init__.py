"""
IPTU API Python SDK
~~~~~~~~~~~~~~~~~~~

SDK oficial para integração com a IPTU API.

Uso básico:

    from iptuapi import IPTUClient

    client = IPTUClient("sua_api_key")
    resultado = client.consulta_endereco("Avenida Paulista", "1000")
    print(resultado)

Com configuração customizada:

    from iptuapi import IPTUClient, ClientConfig, RetryConfig

    config = ClientConfig(
        timeout=60.0,
        retry=RetryConfig(max_retries=5),
        log_requests=True,
    )
    client = IPTUClient("sua_api_key", config=config)

:copyright: (c) 2024-2025 IPTU API
:license: MIT
"""

from .client import IPTUClient, ClientConfig, RetryConfig, Client
from .exceptions import (
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
from .models import (
    CidadeEnum,
    TipoUso,
    PadraoConstrutivo,
    ConsultaEnderecoRequest,
    ConsultaSQLRequest,
    ConsultaCEPRequest,
    ZoneamentoRequest,
    ValuationRequest,
    BatchValuationRequest,
    EnderecoResponse,
    ValoresVenais,
    CaracteristicasImovel,
    HistoricoItem,
    ComparavelItem,
    ZoneamentoResponse,
    IPTUResponse,
    ValuationResponse,
    BatchValuationResponse,
    RateLimitInfo,
    APIResponse,
)

__version__ = "2.0.0"
__all__ = [
    # Client
    "IPTUClient",
    "Client",
    "ClientConfig",
    "RetryConfig",
    # Exceptions
    "IPTUAPIError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
    "TimeoutError",
    "NetworkError",
    "QuotaExceededError",
    "raise_for_status",
    # Enums
    "CidadeEnum",
    "TipoUso",
    "PadraoConstrutivo",
    # Request Models
    "ConsultaEnderecoRequest",
    "ConsultaSQLRequest",
    "ConsultaCEPRequest",
    "ZoneamentoRequest",
    "ValuationRequest",
    "BatchValuationRequest",
    # Response Models
    "EnderecoResponse",
    "ValoresVenais",
    "CaracteristicasImovel",
    "HistoricoItem",
    "ComparavelItem",
    "ZoneamentoResponse",
    "IPTUResponse",
    "ValuationResponse",
    "BatchValuationResponse",
    "RateLimitInfo",
    "APIResponse",
]
