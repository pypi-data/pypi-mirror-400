"""
Parser para normalizar valores de preços de diferentes formatos.
"""

import re
from typing import Union


def parse_price(price_string: Union[str, float, int]) -> float:
    """
    Converte uma string de preço em formato decimal (float).

    Suporta múltiplos formatos:
    - "R$ 1.299,90" → 1299.90
    - "1.299,90" → 1299.90
    - "1,299.90" → 1299.90
    - "$1,299.90" → 1299.90
    - "1299.90" → 1299.90
    - 1299.90 → 1299.90

    Args:
        price_string: String contendo o preço ou número

    Returns:
        Valor do preço em formato decimal

    Raises:
        ValueError: Se o formato não for reconhecido ou valor for inválido
    """
    # Se já é número, retorna
    if isinstance(price_string, (int, float)):
        if price_string < 0:
            raise ValueError("Preço não pode ser negativo")
        return float(price_string)

    if not isinstance(price_string, str):
        raise TypeError(f"Esperado str, int ou float, recebido {type(price_string)}")

    # Remove espaços em branco
    price_string = price_string.strip()

    if not price_string:
        raise ValueError("String de preço vazia")

    # Remove símbolos de moeda e espaços
    # Remove: R$, $, €, £, etc
    cleaned = re.sub(r'[R\$€£¥\s]', '', price_string)

    if not cleaned:
        raise ValueError("String de preço inválida após limpeza")

    # Detecta o formato baseado na última ocorrência de separador
    # Se tiver vírgula depois do último ponto, é formato BR (1.299,90)
    # Se tiver ponto depois da última vírgula, é formato US (1,299.90)

    last_comma = cleaned.rfind(',')
    last_dot = cleaned.rfind('.')

    try:
        if last_comma > last_dot:
            # Formato brasileiro: 1.299,90
            # Remove pontos (separador de milhar) e troca vírgula por ponto
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Formato americano: 1,299.90
            # Remove vírgulas (separador de milhar)
            cleaned = cleaned.replace(',', '')

        value = float(cleaned)

        if value < 0:
            raise ValueError("Preço não pode ser negativo")

        return value

    except ValueError as e:
        raise ValueError(f"Não foi possível converter '{price_string}' para preço: {e}")


def parse_price_range(price_string: str) -> tuple[float, float]:
    """
    Parseia strings de faixa de preço.

    Exemplos:
    - "R$ 100 - R$ 200" → (100.0, 200.0)
    - "100-200" → (100.0, 200.0)

    Args:
        price_string: String contendo a faixa de preço

    Returns:
        Tupla (preço_mínimo, preço_máximo)

    Raises:
        ValueError: Se o formato não for reconhecido
    """
    # Separa por hífen, "a", "até", etc
    parts = re.split(r'\s*[-–—]\s*|\s+a\s+|\s+até\s+', price_string, maxsplit=1)

    if len(parts) != 2:
        raise ValueError(f"Formato de faixa inválido: '{price_string}'")

    min_price = parse_price(parts[0])
    max_price = parse_price(parts[1])

    if min_price > max_price:
        raise ValueError(f"Preço mínimo ({min_price}) maior que máximo ({max_price})")

    return min_price, max_price
