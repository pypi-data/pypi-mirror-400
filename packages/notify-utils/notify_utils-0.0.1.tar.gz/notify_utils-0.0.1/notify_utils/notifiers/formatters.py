"""
Formatadores para exibição de preços e históricos.
"""

from typing import List
from ..models import Price


def format_price(value: float) -> str:
    """
    Formata preço para exibição.

    Regras:
    - Se >= R$ 1: sem centavos (ex: "R$ 1.299")
    - Se < R$ 1: com centavos (ex: "R$ 0,99")
    - Usa separador de milhar (ponto) e decimal (vírgula) padrão BR

    Args:
        value: Valor do preço

    Returns:
        String formatada

    Examples:
        >>> format_price(1299.90)
        'R$ 1.299'
        >>> format_price(899.50)
        'R$ 899'
        >>> format_price(0.99)
        'R$ 0,99'
        >>> format_price(0.50)
        'R$ 0,50'
    """
    if value < 1.0:
        # Produtos baratos: mostra centavos
        return f"R$ {value:.2f}".replace('.', ',')
    else:
        # Produtos >= R$ 1: sem centavos, com separador de milhar
        valor_inteiro = int(round(value))

        # Formata com separador de milhar
        valor_str = f"{valor_inteiro:,}".replace(',', '.')

        return f"R$ {valor_str}"


def get_unique_prices(prices: List[Price], limit: int = 5) -> List[float]:
    """
    Extrai preços únicos de uma lista, ordenados do menor para o maior.

    Args:
        prices: Lista de objetos Price
        limit: Quantidade máxima de preços a retornar

    Returns:
        Lista de valores únicos ordenados (menor para maior)
    """
    if not prices:
        return []

    # Extrai valores e remove duplicatas usando set
    unique_values = list(set(p.value for p in prices))

    # Ordena do menor para o maior
    unique_values.sort()

    # Limita quantidade
    return unique_values[:limit]


def format_price_history(prices: List[Price], limit: int = 5) -> str:
    """
    Formata histórico de preços para exibição.

    Extrai os últimos N preços ÚNICOS, ordena do menor para maior,
    e formata como string separada por vírgulas.

    Args:
        prices: Lista de objetos Price
        limit: Quantidade máxima de preços a mostrar (padrão: 5)

    Returns:
        String formatada (ex: "R$ 899, R$ 999, R$ 1.299")

    Examples:
        >>> prices = [
        ...     Price(value=1399.90, date=datetime.now()),
        ...     Price(value=1299.90, date=datetime.now()),
        ...     Price(value=1299.90, date=datetime.now()),  # duplicata
        ...     Price(value=999.90, date=datetime.now()),
        ...     Price(value=899.90, date=datetime.now()),
        ... ]
        >>> format_price_history(prices, limit=5)
        'R$ 899, R$ 999, R$ 1.299, R$ 1.399'
    """
    if not prices:
        return "Sem historico"

    # Obtém preços únicos ordenados
    unique_values = get_unique_prices(prices, limit)

    if not unique_values:
        return "Sem historico"

    # Formata cada preço e junta com vírgula
    formatted_prices = [format_price(value) for value in unique_values]

    return ", ".join(formatted_prices)
