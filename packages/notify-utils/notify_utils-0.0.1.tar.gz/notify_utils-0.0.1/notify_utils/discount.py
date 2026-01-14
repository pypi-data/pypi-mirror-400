"""
Cálculos de desconto e validação de promoções.
"""

from typing import Optional, List
from .models import Price, PriceHistory, HistoryDiscountResult, DiscountInfo


def calculate_discount_percentage(old_price: float, new_price: float) -> float:
    """
    Calcula o percentual de desconto entre dois preços.

    Formula: ((preço_antigo - preço_novo) / preço_antigo) * 100

    Args:
        old_price: Preço anterior (original)
        new_price: Preço atual (com desconto)

    Returns:
        Percentual de desconto (valores positivos indicam desconto, negativos indicam aumento)

    Raises:
        ValueError: Se algum preço for negativo ou preço antigo for zero
    """
    if old_price < 0 or new_price < 0:
        raise ValueError("Preços não podem ser negativos")

    if old_price == 0:
        raise ValueError("Preço antigo não pode ser zero")

    discount = ((old_price - new_price) / old_price) * 100
    return round(discount, 2)


def calculate_discount_absolute(old_price: float, new_price: float) -> float:
    """
    Calcula o valor absoluto do desconto.

    Args:
        old_price: Preço anterior
        new_price: Preço atual

    Returns:
        Diferença entre os preços (positivo = desconto, negativo = aumento)

    Raises:
        ValueError: Se algum preço for negativo
    """
    if old_price < 0 or new_price < 0:
        raise ValueError("Preços não podem ser negativos")

    return round(old_price - new_price, 2)


def is_real_discount(
    current_price: float,
    advertised_old_price: Optional[float] = None,
    price_history: Optional[List[Price]] = None,
    threshold_percentage: float = 5.0
) -> bool:
    """
    Verifica se um desconto anunciado é real.

    Estratégia:
    - COM histórico: Ignora advertised_old_price, compara preço atual com média histórica
    - SEM histórico: Usa advertised_old_price como referência (primeira vez)

    Args:
        current_price: Preço atual anunciado
        advertised_old_price: Preço "de" anunciado pela loja (usado apenas sem histórico)
        price_history: Lista de preços históricos (opcional, mas prioritário)
        threshold_percentage: Percentual mínimo para considerar desconto real (padrão: 5%)

    Returns:
        True se o desconto for considerado real, False caso contrário

    Raises:
        ValueError: Se não houver histórico nem advertised_old_price
    """
    # Se houver histórico, IGNORA advertised_old_price e usa apenas histórico
    if price_history and len(price_history) > 0:
        # Calcula a média dos preços históricos
        avg_price = sum(p.value for p in price_history) / len(price_history)

        # Calcula o desconto em relação à média histórica
        discount_pct = ((avg_price - current_price) / avg_price) * 100

        # Considera desconto real se for >= threshold_percentage
        return discount_pct >= threshold_percentage

    # Sem histórico: usa advertised_old_price (fallback para primeira vez)
    if advertised_old_price is None:
        raise ValueError("É necessário fornecer advertised_old_price ou price_history")

    # Verifica se há desconto básico
    return current_price < advertised_old_price


def calculate_discount_from_history(
    current_price: float,
    price_history: List[Price],
    period_days: Optional[int] = 30,
    use_median: bool = False,
    skip_recent_days: int = 0
) -> Optional[HistoryDiscountResult]:
    """
    Calcula desconto baseado no histórico de preços (ignora preço "de" anunciado).

    Compara o preço atual com a média (ou mediana) do histórico de um período.

    Args:
        current_price: Preço atual do produto
        price_history: Lista de preços históricos
        period_days: Período em dias para calcular a referência (None = todos os preços)
        use_median: Se True usa mediana, se False usa média (padrão)
        skip_recent_days: Ignora os N dias mais recentes (útil para evitar ruído, padrão: 0)

    Returns:
        HistoryDiscountResult com informações do desconto ou None se não houver histórico suficiente

    Example:
        >>> # Ignora preços de 0-2 dias, usa apenas 3-30 dias
        >>> result = calculate_discount_from_history(
        ...     current_price=899.90,
        ...     price_history=prices,
        ...     period_days=30,
        ...     skip_recent_days=3
        ... )
    """
    if not price_history or len(price_history) == 0:
        return None

    # Importa funções de statistics
    from .statistics import filter_by_period, filter_by_period_range, calculate_mean, calculate_median

    # Filtra por período
    if skip_recent_days > 0 and period_days:
        # Usa intervalo: ignora dias recentes
        filtered_prices = filter_by_period_range(price_history, skip_recent_days, period_days)
    elif period_days:
        # Comportamento padrão: de hoje até period_days
        filtered_prices = filter_by_period(price_history, period_days)
    else:
        # Sem filtro de período
        filtered_prices = price_history

    if not filtered_prices:
        return None

    # Calcula preço de referência (média ou mediana)
    if use_median:
        reference_price = calculate_median(filtered_prices)
        method = 'median'
    else:
        reference_price = calculate_mean(filtered_prices)
        method = 'mean'

    if reference_price is None:
        return None

    # Calcula desconto
    discount_pct = calculate_discount_percentage(reference_price, current_price)
    discount_abs = calculate_discount_absolute(reference_price, current_price)

    return HistoryDiscountResult(
        current_price=current_price,
        reference_price=reference_price,
        discount_percentage=discount_pct,
        discount_absolute=discount_abs,
        is_real_discount=discount_pct > 0,  # Positivo = desconto real
        calculation_method=method,
        period_days=period_days,
        samples_count=len(filtered_prices)
    )


def get_discount_info(
    current_price: float,
    price_history: Optional[List[Price]] = None,
    advertised_old_price: Optional[float] = None,
    period_days: int = 30,
    use_median: bool = False,
    auto_adjust_period: bool = True,
    skip_recent_days: int = 0
) -> DiscountInfo:
    """
    Função inteligente que calcula desconto automaticamente escolhendo a melhor estratégia.

    Estratégia:
    - COM histórico: Usa média/mediana do histórico (ignora advertised_old_price)
    - SEM histórico: Usa advertised_old_price (primeira vez)

    Args:
        current_price: Preço atual do produto
        price_history: Lista de preços históricos (opcional, mas prioritário)
        advertised_old_price: Preço "de" anunciado (usado apenas sem histórico)
        period_days: Período para cálculo da média histórica (padrão: 30 dias)
        use_median: Se True usa mediana, se False usa média
        auto_adjust_period: Se True, ajusta period_days automaticamente para incluir
                           o histórico mais recente (recomendado: True)
        skip_recent_days: Ignora os N dias mais recentes do histórico (padrão: 0)
                         Útil para evitar ruído de dados muito recentes

    Returns:
        DiscountInfo com informações completas do desconto

    Raises:
        ValueError: Se não houver histórico nem advertised_old_price

    Example:
        >>> # Histórico de 33 dias atrás, period_days=30
        >>> prices = [Price(1299.90, datetime.now() - timedelta(days=33))]
        >>> info = get_discount_info(899.90, prices, period_days=30, auto_adjust_period=True)
        >>> info.period_days  # 30 (solicitado)
        >>> info.adjusted_period_days  # 33 (ajustado)
        >>> info.days_since_most_recent  # 33

        >>> # Ignorar preços de 0-2 dias, usar apenas 3-30 dias
        >>> info = get_discount_info(899.90, prices, period_days=30, skip_recent_days=3)
        >>> info.skip_recent_days  # 3
    """
    # Estratégia 1: COM histórico - usa apenas histórico
    if price_history and len(price_history) > 0:
        # Importa funções de statistics
        from .statistics import days_since_most_recent_price, get_recommended_period

        # Calcula dias desde o mais recente
        days_since = days_since_most_recent_price(price_history)

        # Ajusta período se necessário
        actual_period = period_days
        if auto_adjust_period:
            actual_period = get_recommended_period(price_history, period_days)

        history_discount = calculate_discount_from_history(
            current_price=current_price,
            price_history=price_history,
            period_days=actual_period,
            use_median=use_median,
            skip_recent_days=skip_recent_days
        )

        if history_discount:
            return DiscountInfo(
                current_price=history_discount.current_price,
                reference_price=history_discount.reference_price,
                discount_percentage=history_discount.discount_percentage,
                discount_absolute=history_discount.discount_absolute,
                is_real_discount=history_discount.is_real_discount,
                strategy='history',
                has_history=True,
                calculation_method=history_discount.calculation_method,
                period_days=period_days,  # Período solicitado
                samples_count=history_discount.samples_count,
                adjusted_period_days=actual_period if auto_adjust_period else None,
                days_since_most_recent=days_since,
                skip_recent_days=skip_recent_days if skip_recent_days > 0 else None
            )
        else:
            # Se nenhum preço no período, mas temos histórico, use todos os preços
            history_discount = calculate_discount_from_history(
                current_price=current_price,
                price_history=price_history,
                period_days=None,  # Usa todos os preços disponíveis
                use_median=use_median,
                skip_recent_days=0  # Não pula dias quando usa todos
            )

            if history_discount:
                return DiscountInfo(
                    current_price=history_discount.current_price,
                    reference_price=history_discount.reference_price,
                    discount_percentage=history_discount.discount_percentage,
                    discount_absolute=history_discount.discount_absolute,
                    is_real_discount=history_discount.is_real_discount,
                    strategy='history',
                    has_history=True,
                    calculation_method=history_discount.calculation_method,
                    period_days=period_days,  # Período solicitado originalmente
                    samples_count=history_discount.samples_count,
                    adjusted_period_days=None,  # Usou todos os preços, não apenas período
                    days_since_most_recent=days_since,
                    skip_recent_days=None  # Fallback não usa skip
                )

    # Estratégia 2: SEM histórico - usa advertised_old_price
    if advertised_old_price is None:
        raise ValueError("É necessário fornecer price_history ou advertised_old_price")

    discount_pct = calculate_discount_percentage(advertised_old_price, current_price)
    discount_abs = calculate_discount_absolute(advertised_old_price, current_price)

    return DiscountInfo(
        current_price=current_price,
        reference_price=advertised_old_price,
        discount_percentage=discount_pct,
        discount_absolute=discount_abs,
        is_real_discount=discount_pct > 0,  # Assume verdadeiro na primeira vez
        strategy='advertised',
        has_history=False,
        calculation_method='advertised',
        period_days=None,
        samples_count=None,
        adjusted_period_days=None,
        days_since_most_recent=None,
        skip_recent_days=None
    )


def get_best_discount_from_history(price_history: PriceHistory) -> Optional[HistoryDiscountResult]:
    """
    Encontra o maior desconto válido comparando o preço atual com a média histórica.

    DEPRECATED: Use calculate_discount_from_history() ou get_discount_info()

    Args:
        price_history: Histórico de preços do produto

    Returns:
        HistoryDiscountResult com informações do melhor desconto ou None se não houver desconto
    """
    current = price_history.get_current_price()

    if not current or len(price_history.prices) < 2:
        return None

    # Usa calculate_discount_from_history internamente
    historical_prices = price_history.prices[1:]  # Exclui o preço atual

    return calculate_discount_from_history(
        current_price=current.value,
        price_history=historical_prices,
        period_days=None,  # Usa todos os preços históricos
        use_median=False   # Usa média
    )
