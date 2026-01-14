"""
Modelos de dados do SDK IPTU API.

Utiliza Pydantic para validação e serialização de dados.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


class CidadeEnum(str, Enum):
    """Cidades disponíveis na API."""
    SAO_PAULO = "sp"
    BELO_HORIZONTE = "bh"
    RECIFE = "recife"
    PORTO_ALEGRE = "poa"
    FORTALEZA = "fortaleza"
    CURITIBA = "curitiba"
    RIO_DE_JANEIRO = "rj"
    BRASILIA = "brasilia"


class TipoUso(str, Enum):
    """Tipos de uso do imóvel."""
    RESIDENCIAL = "Residencial"
    COMERCIAL = "Comercial"
    INDUSTRIAL = "Industrial"
    MISTO = "Misto"
    TERRENO = "Terreno"


class PadraoConstrutivo(str, Enum):
    """Padrões construtivos."""
    ALTO = "Alto"
    MEDIO = "Médio"
    BAIXO = "Baixo"
    MINIMO = "Mínimo"


# ============================================================================
# Request Models
# ============================================================================

class ConsultaEnderecoRequest(BaseModel):
    """Parâmetros para consulta por endereço."""
    model_config = ConfigDict(populate_by_name=True)

    logradouro: str = Field(..., min_length=3, description="Nome da rua/avenida")
    numero: Optional[str] = Field(None, description="Número do imóvel")
    complemento: Optional[str] = Field(None, description="Complemento (apto, sala)")
    cidade: CidadeEnum = Field(default=CidadeEnum.SAO_PAULO, description="Cidade")
    incluir_historico: bool = Field(default=False, description="Incluir histórico de valores")
    incluir_comparaveis: bool = Field(default=False, description="Incluir imóveis comparáveis")
    incluir_zoneamento: bool = Field(default=False, description="Incluir dados de zoneamento")


class ConsultaSQLRequest(BaseModel):
    """Parâmetros para consulta por SQL."""
    model_config = ConfigDict(populate_by_name=True)

    numero_contribuinte: str = Field(..., description="Número SQL do contribuinte")
    cidade: CidadeEnum = Field(default=CidadeEnum.SAO_PAULO, description="Cidade")
    incluir_historico: bool = Field(default=False)
    incluir_comparaveis: bool = Field(default=False)


class ConsultaCEPRequest(BaseModel):
    """Parâmetros para consulta por CEP."""
    cep: str = Field(..., pattern=r"^\d{5}-?\d{3}$", description="CEP do imóvel")
    cidade: CidadeEnum = Field(default=CidadeEnum.SAO_PAULO)


class ZoneamentoRequest(BaseModel):
    """Parâmetros para consulta de zoneamento."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ValuationRequest(BaseModel):
    """Parâmetros para estimativa de valor (AVM)."""
    model_config = ConfigDict(populate_by_name=True)

    area_terreno: float = Field(..., gt=0, description="Área do terreno em m²")
    area_construida: float = Field(..., ge=0, description="Área construída em m²")
    bairro: str = Field(..., min_length=2, description="Nome do bairro")
    zona: str = Field(..., description="Zona de uso (ex: ZM, ZC)")
    tipo_uso: str = Field(..., description="Tipo de uso do imóvel")
    tipo_padrao: str = Field(..., description="Padrão construtivo")
    ano_construcao: Optional[int] = Field(None, ge=1800, le=2100)
    cidade: CidadeEnum = Field(default=CidadeEnum.SAO_PAULO)


class BatchValuationRequest(BaseModel):
    """Requisição de valuation em lote."""
    imoveis: list[ValuationRequest] = Field(..., min_length=1, max_length=100)


# ============================================================================
# Response Models
# ============================================================================

class EnderecoResponse(BaseModel):
    """Dados de endereço retornados pela API."""
    model_config = ConfigDict(extra="allow")

    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None


class ValoresVenais(BaseModel):
    """Valores venais do imóvel."""
    model_config = ConfigDict(extra="allow")

    valor_venal_terreno: Optional[float] = None
    valor_venal_construcao: Optional[float] = None
    valor_venal_total: Optional[float] = None
    ano_referencia: Optional[int] = None


class CaracteristicasImovel(BaseModel):
    """Características físicas do imóvel."""
    model_config = ConfigDict(extra="allow")

    area_terreno: Optional[float] = None
    area_construida: Optional[float] = None
    testada: Optional[float] = None
    fracao_ideal: Optional[float] = None
    ano_construcao: Optional[int] = None
    quantidade_pavimentos: Optional[int] = None
    tipo_uso: Optional[str] = None
    tipo_padrao: Optional[str] = None


class HistoricoItem(BaseModel):
    """Item do histórico de valores."""
    model_config = ConfigDict(extra="allow")

    ano: int
    valor_venal_terreno: Optional[float] = None
    valor_venal_construcao: Optional[float] = None
    valor_venal_total: Optional[float] = None
    iptu_valor: Optional[float] = None


class ComparavelItem(BaseModel):
    """Imóvel comparável."""
    model_config = ConfigDict(extra="allow")

    sql: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    bairro: Optional[str] = None
    area_terreno: Optional[float] = None
    area_construida: Optional[float] = None
    valor_venal_total: Optional[float] = None
    distancia_metros: Optional[float] = None


class ZoneamentoResponse(BaseModel):
    """Dados de zoneamento."""
    model_config = ConfigDict(extra="allow")

    zona: Optional[str] = None
    zona_descricao: Optional[str] = None
    coeficiente_aproveitamento_basico: Optional[float] = None
    coeficiente_aproveitamento_maximo: Optional[float] = None
    taxa_ocupacao_maxima: Optional[float] = None
    gabarito_maximo: Optional[int] = None


class IPTUResponse(BaseModel):
    """Resposta completa de consulta IPTU."""
    model_config = ConfigDict(extra="allow")

    sql: str = Field(..., description="Número do contribuinte (SQL)")
    endereco: Optional[EnderecoResponse] = None
    valores: Optional[ValoresVenais] = None
    caracteristicas: Optional[CaracteristicasImovel] = None
    historico: Optional[list[HistoricoItem]] = None
    comparaveis: Optional[list[ComparavelItem]] = None
    zoneamento: Optional[ZoneamentoResponse] = None

    # Campos adicionais que podem vir diretamente
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    area_terreno: Optional[float] = None
    area_construida: Optional[float] = None
    valor_venal_terreno: Optional[float] = None
    valor_venal_construcao: Optional[float] = None
    valor_venal_total: Optional[float] = None
    iptu_valor: Optional[float] = None
    ano_construcao: Optional[int] = None
    tipo_uso: Optional[str] = None
    zona: Optional[str] = None


class ValuationResponse(BaseModel):
    """Resposta de estimativa de valor."""
    model_config = ConfigDict(extra="allow")

    valor_estimado: float = Field(..., description="Valor estimado em R$")
    valor_minimo: Optional[float] = Field(None, description="Valor mínimo do intervalo")
    valor_maximo: Optional[float] = Field(None, description="Valor máximo do intervalo")
    confianca: Optional[float] = Field(None, ge=0, le=1, description="Nível de confiança")
    metodo: Optional[str] = Field(None, description="Método de avaliação utilizado")
    comparaveis_utilizados: Optional[int] = None
    data_avaliacao: Optional[datetime] = None


class BatchValuationResponse(BaseModel):
    """Resposta de valuation em lote."""
    resultados: list[ValuationResponse]
    total_processados: int
    total_erros: int
    erros: Optional[list[dict[str, Any]]] = None


class RateLimitInfo(BaseModel):
    """Informações de rate limit."""
    limit: int = Field(..., description="Limite de requisições")
    remaining: int = Field(..., description="Requisições restantes")
    reset: int = Field(..., description="Timestamp de reset")

    @property
    def reset_datetime(self) -> datetime:
        """Retorna datetime do reset."""
        return datetime.fromtimestamp(self.reset)


class APIResponse(BaseModel):
    """Resposta genérica da API com metadados."""
    model_config = ConfigDict(extra="allow")

    data: Any
    rate_limit: Optional[RateLimitInfo] = None
    request_id: Optional[str] = None
    cached: bool = False
