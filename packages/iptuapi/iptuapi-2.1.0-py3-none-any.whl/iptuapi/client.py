"""
Cliente principal do SDK IPTU API.

Suporta operações síncronas e assíncronas com retry automático,
logging, cache e rate limit tracking.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    IPTUAPIError,
    AuthenticationError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
    raise_for_status,
)
from .models import (
    CidadeEnum,
    IPTUResponse,
    RateLimitInfo,
    ValuationResponse,
    ZoneamentoResponse,
)

# Type variable para métodos genéricos
T = TypeVar("T")

# Logger do SDK
logger = logging.getLogger("iptuapi")


@dataclass
class RetryConfig:
    """Configuração de retry."""
    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)
    retry_methods: tuple[str, ...] = ("GET", "POST", "PUT", "DELETE")


@dataclass
class ClientConfig:
    """Configuração do cliente."""
    base_url: str = "https://iptuapi.com.br/api/v1"
    timeout: float = 30.0
    retry: RetryConfig = field(default_factory=RetryConfig)
    user_agent: str = "iptuapi-python/2.1.0"
    verify_ssl: bool = True
    log_requests: bool = False
    log_responses: bool = False


class IPTUClient:
    """
    Cliente para a IPTU API.

    Suporta retry automático, logging e rate limit tracking.

    Args:
        api_key: Sua chave de API (obrigatória)
        config: Configurações do cliente (opcional)
        base_url: URL base da API (shortcut para config.base_url)
        timeout: Timeout em segundos (shortcut para config.timeout)

    Exemplo:
        >>> client = IPTUClient("sua_api_key")
        >>> resultado = client.consulta_endereco("Avenida Paulista", "1000")

        >>> # Com context manager
        >>> with IPTUClient("sua_api_key") as client:
        ...     resultado = client.consulta_endereco("Avenida Paulista")

        >>> # Com configuração customizada
        >>> config = ClientConfig(timeout=60, retry=RetryConfig(max_retries=5))
        >>> client = IPTUClient("sua_api_key", config=config)
    """

    def __init__(
        self,
        api_key: str,
        config: Optional[ClientConfig] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        if not api_key:
            raise ValueError("API Key é obrigatória")

        self.api_key = api_key
        self.config = config or ClientConfig()

        # Sobrescreve com parâmetros diretos se fornecidos
        if base_url:
            self.config.base_url = base_url
        if timeout:
            self.config.timeout = timeout

        # Rate limit tracking
        self._rate_limit: Optional[RateLimitInfo] = None
        self._last_request_id: Optional[str] = None

        # Sessão HTTP com retry configurado
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry e headers padrão."""
        session = requests.Session()

        # Configurar retry
        retry_strategy = Retry(
            total=self.config.retry.max_retries,
            backoff_factor=self.config.retry.backoff_factor,
            status_forcelist=list(self.config.retry.retry_statuses),
            allowed_methods=list(self.config.retry.retry_methods),
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers padrão
        session.headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.config.user_agent,
        })

        return session

    def _log_request(
        self,
        method: str,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> None:
        """Log de requisição se habilitado."""
        if self.config.log_requests:
            logger.info(
                "Request: %s %s | params=%s | json=%s",
                method,
                url,
                params,
                json,
            )

    def _log_response(
        self,
        response: requests.Response,
        elapsed_ms: float,
    ) -> None:
        """Log de resposta se habilitado."""
        if self.config.log_responses:
            logger.info(
                "Response: %s %s | status=%d | elapsed=%.2fms",
                response.request.method,
                response.url,
                response.status_code,
                elapsed_ms,
            )

    def _extract_rate_limit(self, response: requests.Response) -> Optional[RateLimitInfo]:
        """Extrai informações de rate limit dos headers."""
        try:
            limit = response.headers.get("X-RateLimit-Limit")
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")

            if limit and remaining and reset:
                return RateLimitInfo(
                    limit=int(limit),
                    remaining=int(remaining),
                    reset=int(reset),
                )
        except (ValueError, TypeError):
            pass
        return None

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Executa requisição HTTP com tratamento de erros."""
        url = urljoin(self.config.base_url + "/", endpoint.lstrip("/"))

        self._log_request(method, url, params, json)
        start_time = time.monotonic()

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
        except requests.exceptions.Timeout as e:
            raise TimeoutError(timeout_seconds=self.config.timeout) from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(original_error=e) from e
        except requests.exceptions.RequestException as e:
            raise IPTUAPIError(f"Erro na requisição: {e}") from e

        elapsed_ms = (time.monotonic() - start_time) * 1000
        self._log_response(response, elapsed_ms)

        # Atualizar rate limit tracking
        self._rate_limit = self._extract_rate_limit(response)
        self._last_request_id = response.headers.get("X-Request-ID")

        # Processar resposta
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = {"detail": response.text}

            retry_after = None
            if response.status_code == 429:
                retry_after_header = response.headers.get("Retry-After")
                if retry_after_header:
                    try:
                        retry_after = int(retry_after_header)
                    except ValueError:
                        pass

            raise_for_status(
                status_code=response.status_code,
                response_body=body,
                request_id=self._last_request_id,
                retry_after=retry_after,
            )

        return response.json()

    # =========================================================================
    # Propriedades
    # =========================================================================

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Informações de rate limit da última requisição."""
        return self._rate_limit

    @property
    def last_request_id(self) -> Optional[str]:
        """ID da última requisição (útil para suporte)."""
        return self._last_request_id

    # =========================================================================
    # Endpoints de Consulta
    # =========================================================================

    def consulta_endereco(
        self,
        logradouro: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
        incluir_historico: bool = False,
        incluir_comparaveis: bool = False,
        incluir_zoneamento: bool = False,
    ) -> dict[str, Any]:
        """
        Busca dados de IPTU por endereço.

        Args:
            logradouro: Nome da rua/avenida
            numero: Número do imóvel (opcional)
            complemento: Apartamento/sala (opcional)
            cidade: Cidade da consulta (default: São Paulo)
            incluir_historico: Incluir histórico de valores
            incluir_comparaveis: Incluir imóveis similares
            incluir_zoneamento: Incluir dados de zoneamento

        Returns:
            Dados do imóvel encontrado

        Raises:
            NotFoundError: Se o imóvel não for encontrado
            ValidationError: Se os parâmetros forem inválidos
            AuthenticationError: Se a API Key for inválida
            RateLimitError: Se exceder o limite de requisições
        """
        params = {
            "logradouro": logradouro,
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }
        if numero:
            params["numero"] = numero
        if complemento:
            params["complemento"] = complemento
        if incluir_historico:
            params["incluir_historico"] = "true"
        if incluir_comparaveis:
            params["incluir_comparaveis"] = "true"
        if incluir_zoneamento:
            params["incluir_zoneamento"] = "true"

        return self._request("GET", "/consulta/endereco", params=params)

    def consulta_sql(
        self,
        numero_contribuinte: str,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
        incluir_historico: bool = False,
        incluir_comparaveis: bool = False,
    ) -> dict[str, Any]:
        """
        Busca dados de IPTU por número SQL (contribuinte).

        Args:
            numero_contribuinte: Número SQL do imóvel
            cidade: Cidade da consulta
            incluir_historico: Incluir histórico de valores
            incluir_comparaveis: Incluir imóveis similares

        Returns:
            Dados completos do imóvel
        """
        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
            "incluir_historico": str(incluir_historico).lower(),
            "incluir_comparaveis": str(incluir_comparaveis).lower(),
        }

        return self._request(
            "GET",
            f"/consulta/sql/{numero_contribuinte}",
            params=params,
        )

    def consulta_cep(
        self,
        cep: str,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> list[dict[str, Any]]:
        """
        Busca imóveis por CEP.

        Args:
            cep: CEP do imóvel (formato: 00000-000 ou 00000000)
            cidade: Cidade da consulta

        Returns:
            Lista de imóveis no CEP
        """
        # Normalizar CEP
        cep = cep.replace("-", "").strip()

        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }

        return self._request("GET", f"/consulta/cep/{cep}", params=params)

    def consulta_zoneamento(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:
        """
        Consulta zoneamento por coordenadas.

        Args:
            latitude: Latitude do ponto
            longitude: Longitude do ponto

        Returns:
            Dados de zoneamento da localização
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
        }

        return self._request("GET", "/consulta/zoneamento", params=params)

    # =========================================================================
    # Endpoints de Valuation (AVM)
    # =========================================================================

    def valuation_estimate(
        self,
        area_terreno: float,
        area_construida: float,
        bairro: str,
        zona: str,
        tipo_uso: str,
        tipo_padrao: str,
        ano_construcao: Optional[int] = None,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> dict[str, Any]:
        """
        Estima o valor de mercado do imóvel usando ML.

        Disponível apenas para planos Pro e Enterprise.

        Args:
            area_terreno: Área do terreno em m²
            area_construida: Área construída em m²
            bairro: Nome do bairro
            zona: Zona de uso (ex: ZM, ZC)
            tipo_uso: Tipo de uso (Residencial, Comercial, etc)
            tipo_padrao: Padrão construtivo (Alto, Médio, Baixo)
            ano_construcao: Ano de construção (opcional)
            cidade: Cidade da consulta

        Returns:
            Estimativa com valor_estimado, valor_minimo, valor_maximo, confianca

        Raises:
            ForbiddenError: Se o plano não permitir (requer Pro+)
        """
        payload = {
            "area_terreno": area_terreno,
            "area_construida": area_construida,
            "bairro": bairro,
            "zona": zona,
            "tipo_uso": tipo_uso,
            "tipo_padrao": tipo_padrao,
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }
        if ano_construcao:
            payload["ano_construcao"] = ano_construcao

        return self._request("POST", "/valuation/estimate", json=payload)

    def valuation_batch(
        self,
        imoveis: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Valuation em lote (até 100 imóveis).

        Disponível apenas para plano Enterprise.

        Args:
            imoveis: Lista de dicts com dados dos imóveis

        Returns:
            Resultados de valuation para cada imóvel
        """
        return self._request("POST", "/valuation/estimate/batch", json={"imoveis": imoveis})

    def valuation_comparables(
        self,
        bairro: str,
        area_min: float,
        area_max: float,
        tipo_uso: Optional[str] = None,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Busca imóveis comparáveis para análise.

        Args:
            bairro: Nome do bairro
            area_min: Área mínima em m²
            area_max: Área máxima em m²
            tipo_uso: Filtrar por tipo de uso
            cidade: Cidade da consulta
            limit: Número máximo de resultados

        Returns:
            Lista de imóveis comparáveis
        """
        params = {
            "bairro": bairro,
            "area_min": area_min,
            "area_max": area_max,
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
            "limit": limit,
        }
        if tipo_uso:
            params["tipo_uso"] = tipo_uso

        return self._request("GET", "/valuation/comparables", params=params)

    def valuation_statistics(
        self,
        bairro: str,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> dict[str, Any]:
        """
        Estatísticas de valores por bairro.

        Args:
            bairro: Nome do bairro
            cidade: Cidade da consulta

        Returns:
            Estatísticas: média, mediana, min, max, etc
        """
        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }

        return self._request("GET", f"/valuation/statistics/{bairro}", params=params)

    # =========================================================================
    # Endpoints de Dados Externos
    # =========================================================================

    def dados_iptu_historico(
        self,
        numero_contribuinte: str,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> list[dict[str, Any]]:
        """
        Histórico de valores IPTU de um imóvel.

        Args:
            numero_contribuinte: Número SQL do imóvel
            cidade: Cidade da consulta

        Returns:
            Lista com histórico anual de valores
        """
        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }

        return self._request("GET", f"/dados/iptu/historico/{numero_contribuinte}", params=params)

    def dados_ipca(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Índice IPCA histórico.

        Args:
            data_inicio: Data inicial (YYYY-MM)
            data_fim: Data final (YYYY-MM)

        Returns:
            Série histórica do IPCA
        """
        params = {}
        if data_inicio:
            params["data_inicio"] = data_inicio
        if data_fim:
            params["data_fim"] = data_fim

        return self._request("GET", "/dados/ipca", params=params)

    def dados_ipca_corrigir(
        self,
        valor: float,
        data_origem: str,
        data_destino: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Correção monetária pelo IPCA.

        Args:
            valor: Valor a corrigir
            data_origem: Data do valor original (YYYY-MM)
            data_destino: Data destino (default: atual)

        Returns:
            Valor corrigido e fator de correção
        """
        params = {
            "valor": valor,
            "data_origem": data_origem,
        }
        if data_destino:
            params["data_destino"] = data_destino

        return self._request("GET", "/dados/ipca/corrigir", params=params)

    def dados_cnpj(self, cnpj: str) -> dict[str, Any]:
        """
        Consulta dados de empresa por CNPJ.

        Args:
            cnpj: CNPJ da empresa (apenas números)

        Returns:
            Dados cadastrais da empresa
        """
        cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
        return self._request("GET", f"/dados/cnpj/{cnpj}")

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def close(self) -> None:
        """Fecha a sessão HTTP."""
        self._session.close()

    def __enter__(self) -> "IPTUClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"IPTUClient(base_url={self.config.base_url!r})"

    # =========================================================================
    # Endpoints IPTU Tools (Ferramentas IPTU 2026)
    # =========================================================================

    def iptu_tools_cidades(self) -> dict[str, Any]:
        """
        Lista todas as cidades com calendario de IPTU disponivel.

        Returns:
            Lista de cidades com codigo, nome, desconto e parcelas

        Exemplo:
            >>> client.iptu_tools_cidades()
            {"cidades": [...], "total": 7}
        """
        return self._request("GET", "/iptu-tools/cidades")

    def iptu_tools_calendario(
        self,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> dict[str, Any]:
        """
        Retorna o calendario completo de IPTU para a cidade especificada.

        Args:
            cidade: Codigo da cidade (sp, bh, rj, recife, curitiba, poa, fortaleza)

        Returns:
            Calendario com vencimentos, descontos, alertas e novidades

        Exemplo:
            >>> client.iptu_tools_calendario("sp")
            {"cidade": "Sao Paulo", "ano": 2026, "desconto_vista_percentual": 3.0, ...}
        """
        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }
        return self._request("GET", "/iptu-tools/calendario", params=params)

    def iptu_tools_simulador(
        self,
        valor_iptu: float,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
        valor_venal: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        Simula as opcoes de pagamento do IPTU (a vista vs parcelado).

        Args:
            valor_iptu: Valor total do IPTU
            cidade: Codigo da cidade
            valor_venal: Valor venal do imovel (para verificar isencao)

        Returns:
            Comparativo entre pagamento a vista e parcelado com recomendacao

        Exemplo:
            >>> client.iptu_tools_simulador(1500.00, "sp", valor_venal=350000)
            {"valor_original": 1500.00, "valor_vista": 1455.00, "economia_vista": 45.00, ...}
        """
        payload = {
            "valor_iptu": valor_iptu,
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }
        if valor_venal is not None:
            payload["valor_venal"] = valor_venal

        return self._request("POST", "/iptu-tools/simulador", json=payload)

    def iptu_tools_isencao(
        self,
        valor_venal: float,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
    ) -> dict[str, Any]:
        """
        Verifica se um imovel e elegivel para isencao de IPTU.

        Args:
            valor_venal: Valor venal do imovel
            cidade: Codigo da cidade

        Returns:
            Elegibilidade para isencao total ou parcial

        Exemplo:
            >>> client.iptu_tools_isencao(250000, "sp")
            {"elegivel_isencao_total": True, "mensagem": "Seu imovel esta ISENTO...", ...}
        """
        params = {
            "valor_venal": valor_venal,
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
        }
        return self._request("GET", "/iptu-tools/isencao", params=params)

    def iptu_tools_proximo_vencimento(
        self,
        cidade: Union[CidadeEnum, str] = CidadeEnum.SAO_PAULO,
        parcela: int = 1,
    ) -> dict[str, Any]:
        """
        Retorna informacoes sobre o proximo vencimento do IPTU.

        Args:
            cidade: Codigo da cidade
            parcela: Numero da parcela (1-12)

        Returns:
            Data de vencimento, dias restantes e status

        Exemplo:
            >>> client.iptu_tools_proximo_vencimento("sp", parcela=1)
            {"data_vencimento": "2026-02-09", "dias_restantes": 32, "status": "em_dia", ...}
        """
        params = {
            "cidade": cidade.value if isinstance(cidade, CidadeEnum) else cidade,
            "parcela": parcela,
        }
        return self._request("GET", "/iptu-tools/proximo-vencimento", params=params)



# Alias para compatibilidade
Client = IPTUClient
