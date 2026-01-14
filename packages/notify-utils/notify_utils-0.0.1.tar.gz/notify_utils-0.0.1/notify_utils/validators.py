"""
Validadores para preços e dados relacionados.
"""

from datetime import datetime
from typing import Union


def validate_price(value: Union[float, int]) -> bool:
    """
    Valida se um valor de preço é válido.

    Args:
        value: Valor a ser validado

    Returns:
        True se válido, False caso contrário
    """
    if not isinstance(value, (int, float)):
        return False

    return value >= 0


def validate_currency(currency: str) -> bool:
    """
    Valida se um código de moeda é válido (formato básico).

    Args:
        currency: Código da moeda (ex: "BRL", "USD")

    Returns:
        True se válido, False caso contrário
    """
    if not isinstance(currency, str):
        return False

    # Códigos de moeda geralmente têm 3 letras maiúsculas
    return len(currency) == 3 and currency.isupper() and currency.isalpha()


def validate_date(date: datetime) -> bool:
    """
    Valida se uma data é válida e não está no futuro.

    Args:
        date: Data a ser validada

    Returns:
        True se válida, False caso contrário
    """
    if not isinstance(date, datetime):
        return False

    # Não aceita datas futuras
    return date <= datetime.now()


def validate_discount_percentage(percentage: float) -> bool:
    """
    Valida se um percentual de desconto é razoável.

    Args:
        percentage: Percentual de desconto

    Returns:
        True se válido (entre -100 e 100), False caso contrário
    """
    if not isinstance(percentage, (int, float)):
        return False

    # Permite de -100% (aumento de 100%) até 100% (desconto de 100%)
    return -100 <= percentage <= 100


def is_suspicious_discount(
    current_price: float,
    advertised_old_price: float,
    min_percentage: float = 70.0
) -> bool:
    """
    Verifica se um desconto é suspeito (muito alto).

    Descontos acima de 70% geralmente são suspeitos de fraude.

    Args:
        current_price: Preço atual
        advertised_old_price: Preço "de" anunciado
        min_percentage: Percentual mínimo para considerar suspeito (padrão: 70%)

    Returns:
        True se suspeito, False caso contrário
    """
    if current_price >= advertised_old_price:
        return False

    discount_pct = ((advertised_old_price - current_price) / advertised_old_price) * 100
    return discount_pct >= min_percentage
