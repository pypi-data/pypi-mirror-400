"""
Tests for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError as PydanticValidationError

from iptuapi import (
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


class TestEnums:
    """Tests for enum types."""

    def test_cidade_enum_values(self):
        """Test CidadeEnum values."""
        assert CidadeEnum.SAO_PAULO.value == "sp"
        assert CidadeEnum.BELO_HORIZONTE.value == "bh"
        assert CidadeEnum.RECIFE.value == "recife"

    def test_tipo_uso_values(self):
        """Test TipoUso values."""
        assert TipoUso.RESIDENCIAL.value == "Residencial"
        assert TipoUso.COMERCIAL.value == "Comercial"
        assert TipoUso.INDUSTRIAL.value == "Industrial"

    def test_padrao_construtivo_values(self):
        """Test PadraoConstrutivo values."""
        assert PadraoConstrutivo.ALTO.value == "Alto"
        assert PadraoConstrutivo.MEDIO.value == "Médio"
        assert PadraoConstrutivo.BAIXO.value == "Baixo"


class TestConsultaEnderecoRequest:
    """Tests for ConsultaEnderecoRequest."""

    def test_valid_request(self):
        """Test valid request creation."""
        req = ConsultaEnderecoRequest(
            logradouro="Avenida Paulista",
            numero="1000",
            cidade=CidadeEnum.SAO_PAULO,
        )
        assert req.logradouro == "Avenida Paulista"
        assert req.numero == "1000"
        assert req.cidade == CidadeEnum.SAO_PAULO

    def test_default_values(self):
        """Test default values."""
        req = ConsultaEnderecoRequest(logradouro="Avenida Paulista")
        assert req.cidade == CidadeEnum.SAO_PAULO
        assert req.incluir_historico is False
        assert req.incluir_comparaveis is False
        assert req.incluir_zoneamento is False

    def test_logradouro_min_length(self):
        """Test logradouro minimum length validation."""
        with pytest.raises(PydanticValidationError):
            ConsultaEnderecoRequest(logradouro="AB")

    def test_optional_fields(self):
        """Test optional fields."""
        req = ConsultaEnderecoRequest(
            logradouro="Avenida Paulista",
            complemento="Sala 501",
            incluir_historico=True,
        )
        assert req.complemento == "Sala 501"
        assert req.incluir_historico is True


class TestConsultaSQLRequest:
    """Tests for ConsultaSQLRequest."""

    def test_valid_request(self):
        """Test valid request creation."""
        req = ConsultaSQLRequest(numero_contribuinte="000.000.0000-0")
        assert req.numero_contribuinte == "000.000.0000-0"
        assert req.cidade == CidadeEnum.SAO_PAULO


class TestConsultaCEPRequest:
    """Tests for ConsultaCEPRequest."""

    def test_valid_cep_with_dash(self):
        """Test valid CEP with dash."""
        req = ConsultaCEPRequest(cep="01310-100")
        assert req.cep == "01310-100"

    def test_valid_cep_without_dash(self):
        """Test valid CEP without dash."""
        req = ConsultaCEPRequest(cep="01310100")
        assert req.cep == "01310100"

    def test_invalid_cep(self):
        """Test invalid CEP."""
        with pytest.raises(PydanticValidationError):
            ConsultaCEPRequest(cep="123")


class TestZoneamentoRequest:
    """Tests for ZoneamentoRequest."""

    def test_valid_coordinates(self):
        """Test valid coordinates."""
        req = ZoneamentoRequest(latitude=-23.5505, longitude=-46.6333)
        assert req.latitude == -23.5505
        assert req.longitude == -46.6333

    def test_latitude_bounds(self):
        """Test latitude bounds validation."""
        with pytest.raises(PydanticValidationError):
            ZoneamentoRequest(latitude=91.0, longitude=0.0)

    def test_longitude_bounds(self):
        """Test longitude bounds validation."""
        with pytest.raises(PydanticValidationError):
            ZoneamentoRequest(latitude=0.0, longitude=181.0)


class TestValuationRequest:
    """Tests for ValuationRequest."""

    def test_valid_request(self):
        """Test valid valuation request."""
        req = ValuationRequest(
            area_terreno=500.0,
            area_construida=1200.0,
            bairro="Bela Vista",
            zona="ZC",
            tipo_uso="Comercial",
            tipo_padrao="Alto",
        )
        assert req.area_terreno == 500.0
        assert req.bairro == "Bela Vista"

    def test_area_terreno_must_be_positive(self):
        """Test area_terreno must be positive."""
        with pytest.raises(PydanticValidationError):
            ValuationRequest(
                area_terreno=0.0,
                area_construida=100.0,
                bairro="Test",
                zona="ZC",
                tipo_uso="Residencial",
                tipo_padrao="Médio",
            )

    def test_ano_construcao_bounds(self):
        """Test ano_construcao bounds."""
        with pytest.raises(PydanticValidationError):
            ValuationRequest(
                area_terreno=100.0,
                area_construida=100.0,
                bairro="Test",
                zona="ZC",
                tipo_uso="Residencial",
                tipo_padrao="Médio",
                ano_construcao=1799,
            )


class TestBatchValuationRequest:
    """Tests for BatchValuationRequest."""

    def test_valid_batch(self):
        """Test valid batch request."""
        imoveis = [
            ValuationRequest(
                area_terreno=100.0,
                area_construida=200.0,
                bairro="Bela Vista",
                zona="ZC",
                tipo_uso="Comercial",
                tipo_padrao="Alto",
            )
        ]
        req = BatchValuationRequest(imoveis=imoveis)
        assert len(req.imoveis) == 1

    def test_empty_batch_invalid(self):
        """Test empty batch is invalid."""
        with pytest.raises(PydanticValidationError):
            BatchValuationRequest(imoveis=[])


class TestResponseModels:
    """Tests for response models."""

    def test_endereco_response(self):
        """Test EnderecoResponse."""
        resp = EnderecoResponse(
            logradouro="Avenida Paulista",
            numero="1000",
            bairro="Bela Vista",
        )
        assert resp.logradouro == "Avenida Paulista"
        assert resp.cep is None  # Optional

    def test_valores_venais(self):
        """Test ValoresVenais."""
        resp = ValoresVenais(
            valor_venal_terreno=1000000.0,
            valor_venal_construcao=500000.0,
            valor_venal_total=1500000.0,
        )
        assert resp.valor_venal_total == 1500000.0

    def test_caracteristicas_imovel(self):
        """Test CaracteristicasImovel."""
        resp = CaracteristicasImovel(
            area_terreno=500.0,
            area_construida=1200.0,
            ano_construcao=1985,
        )
        assert resp.area_terreno == 500.0

    def test_historico_item(self):
        """Test HistoricoItem."""
        item = HistoricoItem(
            ano=2023,
            valor_venal_total=1500000.0,
            iptu_valor=5000.0,
        )
        assert item.ano == 2023

    def test_comparavel_item(self):
        """Test ComparavelItem."""
        item = ComparavelItem(
            sql="000.000.0001-0",
            logradouro="Rua Teste",
            distancia_metros=150.0,
        )
        assert item.distancia_metros == 150.0

    def test_zoneamento_response(self):
        """Test ZoneamentoResponse."""
        resp = ZoneamentoResponse(
            zona="ZM",
            zona_descricao="Zona Mista",
            coeficiente_aproveitamento_basico=1.0,
        )
        assert resp.zona == "ZM"

    def test_iptu_response(self):
        """Test IPTUResponse."""
        resp = IPTUResponse(
            sql="000.000.0000-0",
            logradouro="Avenida Paulista",
            valor_venal_total=4300000.0,
        )
        assert resp.sql == "000.000.0000-0"

    def test_iptu_response_with_nested_objects(self):
        """Test IPTUResponse with nested objects."""
        resp = IPTUResponse(
            sql="000.000.0000-0",
            endereco=EnderecoResponse(logradouro="Avenida Paulista"),
            valores=ValoresVenais(valor_venal_total=4300000.0),
        )
        assert resp.endereco.logradouro == "Avenida Paulista"
        assert resp.valores.valor_venal_total == 4300000.0

    def test_valuation_response(self):
        """Test ValuationResponse."""
        resp = ValuationResponse(
            valor_estimado=5000000.0,
            valor_minimo=4500000.0,
            valor_maximo=5500000.0,
            confianca=0.85,
        )
        assert resp.valor_estimado == 5000000.0
        assert resp.confianca == 0.85

    def test_batch_valuation_response(self):
        """Test BatchValuationResponse."""
        resultados = [
            ValuationResponse(valor_estimado=1000000.0),
            ValuationResponse(valor_estimado=2000000.0),
        ]
        resp = BatchValuationResponse(
            resultados=resultados,
            total_processados=2,
            total_erros=0,
        )
        assert len(resp.resultados) == 2
        assert resp.total_processados == 2


class TestRateLimitInfo:
    """Tests for RateLimitInfo."""

    def test_rate_limit_info(self):
        """Test RateLimitInfo creation."""
        info = RateLimitInfo(
            limit=1000,
            remaining=999,
            reset=1704067200,
        )
        assert info.limit == 1000
        assert info.remaining == 999

    def test_reset_datetime_property(self):
        """Test reset_datetime property."""
        info = RateLimitInfo(
            limit=1000,
            remaining=999,
            reset=1704067200,  # 2024-01-01 00:00:00 UTC
        )
        dt = info.reset_datetime
        assert isinstance(dt, datetime)
        # Check the datetime is valid (year can vary based on timezone)
        assert dt.year in (2023, 2024)  # Allow both due to timezone differences


class TestAPIResponse:
    """Tests for APIResponse."""

    def test_api_response(self):
        """Test APIResponse creation."""
        resp = APIResponse(
            data={"key": "value"},
            request_id="req_123",
            cached=True,
        )
        assert resp.data == {"key": "value"}
        assert resp.request_id == "req_123"
        assert resp.cached is True

    def test_api_response_with_rate_limit(self):
        """Test APIResponse with rate limit info."""
        resp = APIResponse(
            data={},
            rate_limit=RateLimitInfo(limit=1000, remaining=999, reset=1704067200),
        )
        assert resp.rate_limit.limit == 1000


class TestModelExtraFields:
    """Tests for extra field handling."""

    def test_response_allows_extra_fields(self):
        """Test response models allow extra fields."""
        resp = IPTUResponse(
            sql="000.000.0000-0",
            campo_extra="valor extra",
        )
        assert resp.sql == "000.000.0000-0"
        # Extra field should be accessible
        assert resp.campo_extra == "valor extra"
