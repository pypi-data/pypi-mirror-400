# IPTU API - Python SDK

SDK oficial Python para integracao com a IPTU API. Acesso a dados de IPTU de Sao Paulo, Belo Horizonte e Recife.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## Instalacao

```bash
pip install iptuapi
```

## Uso Rapido

```python
from iptuapi import IPTUClient

client = IPTUClient("sua_api_key")

# Consulta por endereco
resultado = client.consulta_endereco("Avenida Paulista", "1000")
print(resultado)

# Consulta por SQL (Starter+)
dados = client.consulta_sql("100-01-001-001")
```

## Configuracao

### Cliente Basico

```python
from iptuapi import IPTUClient

client = IPTUClient("sua_api_key")
```

### Configuracao Avancada

```python
from iptuapi import IPTUClient, ClientConfig, RetryConfig
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Configuracao de retry
retry_config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_factor=2.0,
    retryable_status_codes=[429, 500, 502, 503, 504]
)

# Configuracao do cliente
config = ClientConfig(
    base_url="https://iptuapi.com.br/api/v1",
    timeout=60.0,
    retry_config=retry_config
)

client = IPTUClient("sua_api_key", config)
```

### Uso com Context Manager

```python
with IPTUClient("sua_api_key") as client:
    resultado = client.consulta_endereco("Avenida Paulista", "1000")
```

### Cliente Assincrono

```python
import asyncio
from iptuapi import AsyncIPTUClient

async def main():
    async with AsyncIPTUClient("sua_api_key") as client:
        resultado = await client.consulta_endereco("Avenida Paulista", "1000")
        print(resultado)

asyncio.run(main())
```

## Endpoints da API

### Consultas (Todos os Planos)

```python
# Consulta por endereco
resultado = client.consulta_endereco(
    logradouro="Avenida Paulista",
    numero="1000",
    cidade="sp"
)

# Consulta por CEP
resultado = client.consulta_cep("01310-100", cidade="sp")

# Consulta por coordenadas (zoneamento)
resultado = client.consulta_zoneamento(latitude=-23.5505, longitude=-46.6333)
```

### Consultas Avancadas (Starter+)

```python
# Consulta por numero SQL
resultado = client.consulta_sql("100-01-001-001", cidade="sp")

# Historico de valores IPTU
historico = client.dados_iptu_historico("100-01-001-001", cidade="sp")

# Consulta CNPJ
empresa = client.dados_cnpj("12345678000100")

# Correcao monetaria IPCA
corrigido = client.dados_ipca_corrigir(
    valor=100000,
    data_origem="2020-01",
    data_destino="2024-01"
)
```

### Valuation (Pro+)

```python
# Estimativa de valor de mercado
avaliacao = client.valuation_estimate({
    "area_terreno": 250,
    "area_construida": 180,
    "bairro": "Pinheiros",
    "zona": "ZM",
    "tipo_uso": "Residencial",
    "tipo_padrao": "Medio",
    "ano_construcao": 2010
})
print(f"Valor estimado: R$ {avaliacao['valor_estimado']:,.2f}")

# Buscar comparaveis
comparaveis = client.valuation_comparables(
    bairro="Pinheiros",
    area_min=150,
    area_max=250,
    cidade="sp",
    limit=10
)
```

### Batch Operations (Enterprise)

```python
# Valuation em lote (ate 100 imoveis)
imoveis = [
    {"area_terreno": 250, "area_construida": 180, "bairro": "Pinheiros"},
    {"area_terreno": 300, "area_construida": 200, "bairro": "Moema"},
]
resultados = client.valuation_batch(imoveis)
```

## Tratamento de Erros

```python
from iptuapi import (
    IPTUClient,
    IPTUAPIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    TimeoutError,
    NetworkError
)

client = IPTUClient("sua_api_key")

try:
    resultado = client.consulta_endereco("Rua Teste", "100")
except AuthenticationError as e:
    print(f"API Key invalida: {e}")
except ForbiddenError as e:
    print(f"Plano nao autorizado: {e.required_plan}")
except NotFoundError as e:
    print(f"Imovel nao encontrado: {e}")
except RateLimitError as e:
    print(f"Rate limit excedido. Retry em {e.retry_after}s")
except ValidationError as e:
    print(f"Parametros invalidos: {e.errors}")
except ServerError as e:
    print(f"Erro no servidor (retryable): {e}")
except TimeoutError as e:
    print(f"Timeout apos {e.timeout}s")
except NetworkError as e:
    print(f"Erro de conexao: {e}")
except IPTUAPIError as e:
    print(f"Erro generico: {e}, Request ID: {e.request_id}")
```

### Propriedades dos Erros

```python
try:
    resultado = client.consulta_endereco("Rua Teste", "100")
except IPTUAPIError as e:
    print(f"Status Code: {e.status_code}")
    print(f"Request ID: {e.request_id}")
    print(f"Retryable: {e.is_retryable}")
```

## Rate Limiting

```python
# Verificar rate limit apos requisicao
rate_limit = client.rate_limit
if rate_limit:
    print(f"Limite: {rate_limit.limit}")
    print(f"Restantes: {rate_limit.remaining}")
    print(f"Reset em: {rate_limit.reset_at}")

# ID da ultima requisicao (util para suporte)
print(f"Request ID: {client.last_request_id}")
```

## Modelos de Dados

```python
from iptuapi.models import (
    PropertyData,
    ValuationResult,
    RateLimitInfo,
    Address,
    ZoningInfo
)

# Dados tipados com Pydantic
resultado: PropertyData = client.consulta_endereco("Av Paulista", "1000")
print(f"SQL: {resultado.sql}")
print(f"Bairro: {resultado.bairro}")
print(f"Valor Venal: {resultado.valor_venal}")
```

## Logging

```python
import logging

# Habilitar logging de debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("iptuapi")

# Logs incluem:
# - Requisicoes enviadas
# - Respostas recebidas
# - Retries automaticos
# - Rate limit info
```

## Testes

```bash
# Rodar testes
pytest

# Com coverage
pytest --cov=iptuapi

# Testes especificos
pytest tests/test_client.py -v
```

## Cidades Suportadas

| Codigo | Cidade |
|--------|--------|
| sp | Sao Paulo |
| bh | Belo Horizonte |
| recife | Recife |

## Licenca

Copyright (c) 2025-2026 IPTU API. Todos os direitos reservados.

Este software e propriedade exclusiva da IPTU API. O uso esta sujeito aos termos de servico disponiveis em https://iptuapi.com.br/termos

## Links

- [Documentacao](https://iptuapi.com.br/docs)
- [API Reference](https://iptuapi.com.br/docs/api)
- [Portal do Desenvolvedor](https://iptuapi.com.br/dashboard)
