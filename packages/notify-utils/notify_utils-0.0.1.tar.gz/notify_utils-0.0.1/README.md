# notify-utils

Biblioteca Python para parsing de preços de scraping, cálculo de descontos e análise estatística de histórico de preços.

## Funcionalidades

- **Parser de Preços**: Normaliza strings de preços de diferentes formatos (BR, US)
- **Cálculo de Descontos**: Detecta descontos reais vs anunciados usando histórico
- **Análise Estatística**: Média, mediana, tendências e volatilidade de preços
- **Validação de Preços**: Sistema inteligente para validar preços antes de adicionar ao histórico
- **Notificações Discord**: Envio de alertas de preço via webhook (opcional)

## Instalação

```bash
pip install notify-utils
```

## Uso Básico

### Parsing de Preços

```python
from notify_utils import parse_price

preco = parse_price("R$ 1.299,90")  # → 1299.90
preco = parse_price("$1,299.90")    # → 1299.90
```

### Cálculo de Desconto com Histórico

```python
from notify_utils import Price, get_discount_info
from datetime import datetime, timedelta

# Histórico de preços
precos = [
    Price(value=1299.90, date=datetime.now() - timedelta(days=60)),
    Price(value=1199.90, date=datetime.now() - timedelta(days=30)),
]

# Calcular desconto real baseado no histórico
info = get_discount_info(
    current_price=899.90,
    price_history=precos,
    period_days=30
)

print(f"Desconto real: {info.discount_percentage:.2f}%")
print(f"É desconto real? {info.is_real_discount}")
```

### Análise de Tendência

```python
from notify_utils import calculate_price_trend

trend = calculate_price_trend(precos, days=30)

print(f"Direção: {trend.direction}")  # 'increasing', 'decreasing', 'stable'
print(f"Mudança: {trend.change_percentage:.2f}%")
print(f"Confiança: {trend.confidence}")
```

### Validação de Preços

```python
from notify_utils import PriceHistory, Price, PriceAdditionStrategy

history = PriceHistory(product_id="PROD123", prices=precos)

# Validar antes de adicionar
novo_preco = Price(value=899.90, date=datetime.now())
result = history.add_price(
    novo_preco,
    strategy=PriceAdditionStrategy.SMART
)

if result.action.value == "added":
    print(f"Preço adicionado: R$ {result.affected_price.value:.2f}")
```

### Notificações Discord

```python
from notify_utils import Product, DiscordEmbedBuilder

produto = Product(
    product_id="PROD123",
    name="Notebook Gamer",
    url="https://loja.com/produto"
)

builder = DiscordEmbedBuilder()
embed = builder.build_embed(produto, info, precos)
# Enviar via webhook Discord
```

## Documentação Completa

Para mais detalhes, consulte o arquivo [CLAUDE.md](CLAUDE.md) na raiz do projeto.

## Requisitos

- Python >= 3.12
- discord-webhook >= 1.4.1 (opcional, apenas para notificações)

## Licença

MIT
