"""
Análise estatística de histórico de preços.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from statistics import mean, median as median_builtin, stdev
from .models import Price, PriceTrend


def days_since_most_recent_price(prices: List[Price]) -> Optional[int]:
    """
    Calcula quantos dias se passaram desde o preço mais recente até hoje.

    Útil para verificar se o histórico está desatualizado e ajustar
    o período de análise dinamicamente.

    Args:
        prices: Lista de preços

    Returns:
        Número de dias desde o preço mais recente (arredondado para cima)
        ou None se a lista estiver vazia

    Example:
        >>> prices = [Price(100.0, datetime.now() - timedelta(days=33))]
        >>> days_since_most_recent_price(prices)
        33
    """
    if not prices:
        return None

    # Encontra o preço mais recente
    most_recent = max(prices, key=lambda p: p.date)

    # Calcula diferença em dias (arredonda para cima)
    time_diff = datetime.now() - most_recent.date
    days_diff = int(time_diff.total_seconds() / 86400)  # 86400 segundos em um dia

    # Arredonda para cima se houver fração de dia
    if time_diff.total_seconds() % 86400 > 0:
        days_diff += 1

    return days_diff


def get_recommended_period(prices: List[Price], desired_period: int) -> int:
    """
    Retorna o período recomendado que garante incluir o histórico mais recente.

    Se o preço mais recente for mais antigo que o período desejado,
    retorna o número de dias necessário para incluí-lo.

    Args:
        prices: Lista de preços
        desired_period: Período desejado em dias

    Returns:
        Período ajustado que inclui o histórico mais recente

    Example:
        >>> # Histórico mais recente tem 33 dias
        >>> prices = [Price(100.0, datetime.now() - timedelta(days=33))]
        >>> get_recommended_period(prices, 30)
        33  # Ajustado para incluir o histórico

        >>> # Histórico recente tem 20 dias
        >>> prices = [Price(100.0, datetime.now() - timedelta(days=20))]
        >>> get_recommended_period(prices, 30)
        30  # Mantém período desejado
    """
    if not prices:
        return desired_period

    days_since = days_since_most_recent_price(prices)

    if days_since is None:
        return desired_period

    # Retorna o maior entre o período desejado e dias desde o mais recente
    return max(desired_period, days_since)


def filter_by_period_range(
    prices: List[Price],
    start_days: int,
    end_days: int
) -> List[Price]:
    """
    Filtra preços por um intervalo de dias (ignorando dias muito recentes).

    Útil para ignorar ruído de dados muito recentes (mesmo dia, próximos dias).

    Args:
        prices: Lista de preços
        start_days: Começa N dias atrás (ex: 3 = ignora 0, 1, 2 dias)
        end_days: Termina M dias atrás (ex: 30 = até 30 dias atrás)

    Returns:
        Lista de preços entre [hoje-end_days ... hoje-start_days]

    Raises:
        ValueError: Se start_days < 0, end_days <= 0, ou start_days >= end_days

    Example:
        >>> # Ignora preços de 0-2 dias, usa apenas 3-30 dias
        >>> filtered = filter_by_period_range(prices, start_days=3, end_days=30)
        >>> # Retorna preços entre hoje-30d e hoje-3d
    """
    if start_days < 0:
        raise ValueError("start_days deve ser >= 0")
    if end_days <= 0:
        raise ValueError("end_days deve ser > 0")
    if start_days >= end_days:
        raise ValueError("start_days deve ser menor que end_days")

    now = datetime.now()
    start_date = now - timedelta(days=start_days)  # Data mais recente permitida
    end_date = now - timedelta(days=end_days)      # Data mais antiga permitida

    # Filtra preços entre end_date (mais antigo) e start_date (mais recente)
    return [p for p in prices if end_date <= p.date <= start_date]


def filter_by_period(prices: List[Price], days: int) -> List[Price]:
    """
    Filtra preços por período de dias a partir de hoje.

    Args:
        prices: Lista de preços
        days: Número de dias para filtrar (ex: 7, 30, 90)

    Returns:
        Lista de preços dentro do período especificado
    """
    if days <= 0:
        raise ValueError("Número de dias deve ser positivo")

    cutoff_date = datetime.now() - timedelta(days=days)
    return [p for p in prices if p.date >= cutoff_date]


def calculate_mean(prices: List[Price], days: Optional[int] = None) -> Optional[float]:
    """
    Calcula a média de preços.

    Args:
        prices: Lista de preços
        days: Número de dias para filtrar (opcional, se None considera todos os preços)

    Returns:
        Média dos preços ou None se lista vazia

    Raises:
        ValueError: Se days for <= 0
    """
    if not prices:
        return None

    filtered_prices = filter_by_period(prices, days) if days else prices

    if not filtered_prices:
        return None

    values = [p.value for p in filtered_prices]
    return round(mean(values), 2)


def calculate_median(prices: List[Price], days: Optional[int] = None) -> Optional[float]:
    """
    Calcula a mediana de preços.

    Args:
        prices: Lista de preços
        days: Número de dias para filtrar (opcional, se None considera todos os preços)

    Returns:
        Mediana dos preços ou None se lista vazia

    Raises:
        ValueError: Se days for <= 0
    """
    if not prices:
        return None

    filtered_prices = filter_by_period(prices, days) if days else prices

    if not filtered_prices:
        return None

    values = [p.value for p in filtered_prices]
    return round(median_builtin(values), 2)


def get_min_max(
    prices: List[Price],
    days: Optional[int] = None
) -> Optional[tuple[float, float]]:
    """
    Retorna o preço mínimo e máximo do período.

    Args:
        prices: Lista de preços
        days: Número de dias para filtrar (opcional)

    Returns:
        Tupla (preço_mínimo, preço_máximo) ou None se lista vazia

    Raises:
        ValueError: Se days for <= 0
    """
    if not prices:
        return None

    filtered_prices = filter_by_period(prices, days) if days else prices

    if not filtered_prices:
        return None

    values = [p.value for p in filtered_prices]
    return round(min(values), 2), round(max(values), 2)


def calculate_price_statistics(
    prices: List[Price],
    days: Optional[int] = None
) -> Optional[dict]:
    """
    Calcula estatísticas completas de preços.

    Args:
        prices: Lista de preços
        days: Número de dias para filtrar (opcional)

    Returns:
        Dicionário com estatísticas ou None se lista vazia:
        {
            'mean': float,
            'median': float,
            'min': float,
            'max': float,
            'count': int,
            'period_days': int or None
        }

    Raises:
        ValueError: Se days for <= 0
    """
    if not prices:
        return None

    filtered_prices = filter_by_period(prices, days) if days else prices

    if not filtered_prices:
        return None

    values = [p.value for p in filtered_prices]

    return {
        'mean': round(mean(values), 2),
        'median': round(median_builtin(values), 2),
        'min': round(min(values), 2),
        'max': round(max(values), 2),
        'count': len(values),
        'period_days': days
    }


def calculate_volatility(prices: List[Price]) -> Optional[float]:
    """
    Calcula a volatilidade (desvio padrão) dos preços.

    Args:
        prices: Lista de preços

    Returns:
        Desvio padrão dos preços ou None se lista vazia ou com apenas 1 item
    """
    if not prices or len(prices) < 2:
        return None

    values = [p.value for p in prices]
    try:
        return round(stdev(values), 2)
    except:
        return None


def calculate_price_trend(
    prices: List[Price],
    days: int = 30,
    stability_threshold: float = 5.0
) -> Optional[PriceTrend]:
    """
    Analisa a tendência de preço com informações detalhadas.

    Compara a média dos últimos N dias com a média do período anterior
    e retorna análise completa incluindo volatilidade e confiança.

    Args:
        prices: Lista de preços
        days: Período em dias para análise (padrão: 30)
        stability_threshold: % de mudança para considerar estável (padrão: 5.0)

    Returns:
        PriceTrend com análise detalhada ou None se não houver dados suficientes
    """
    if len(prices) < 2:
        return None

    # Divide em dois períodos
    recent_prices = filter_by_period(prices, days)
    cutoff_date = datetime.now() - timedelta(days=days)
    older_cutoff = cutoff_date - timedelta(days=days)
    older_prices = [p for p in prices if older_cutoff <= p.date < cutoff_date]

    if not recent_prices or not older_prices:
        return None

    # Calcula médias
    recent_mean = mean([p.value for p in recent_prices])
    older_mean = mean([p.value for p in older_prices])

    # Calcula mudança percentual (positivo = aumento, negativo = queda)
    change_pct = ((recent_mean - older_mean) / older_mean) * 100

    # Determina direção
    if abs(change_pct) < stability_threshold:
        direction = "stable"
    elif change_pct > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    # Calcula volatilidade (de todos os preços dos dois períodos)
    all_period_prices = recent_prices + older_prices
    volatility = calculate_volatility(all_period_prices) or 0.0

    # Determina se está acelerando (mudança > 10%)
    is_accelerating = abs(change_pct) >= 10.0

    # Calcula confiança baseado na quantidade de amostras
    total_samples = len(recent_prices) + len(older_prices)
    if total_samples >= 20:
        confidence = "high"
    elif total_samples >= 10:
        confidence = "medium"
    else:
        confidence = "low"

    return PriceTrend(
        direction=direction,
        change_percentage=round(change_pct, 2),
        recent_avg=round(recent_mean, 2),
        previous_avg=round(older_mean, 2),
        volatility=volatility,
        confidence=confidence,
        samples_recent=len(recent_prices),
        samples_previous=len(older_prices),
        is_accelerating=is_accelerating,
        analysis_period_days=days
    )
