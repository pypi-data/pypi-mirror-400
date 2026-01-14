"""
notify-utils

Biblioteca para parsing de preços, cálculo de descontos e análise estatística de histórico de preços.
"""

from .models import (
    Product,
    Price,
    PriceHistory,
    DiscountResult,
    HistoryDiscountResult,
    DiscountInfo,
    PriceTrend,
    PriceComparisonStatus,
    PriceAction,
    PriceAdditionStrategy,
    PriceComparisonResult
)
from .parser import parse_price
from .discount import (
    calculate_discount_percentage,
    calculate_discount_absolute,
    is_real_discount,
    calculate_discount_from_history,
    get_discount_info,
    get_best_discount_from_history
)
from .statistics import (
    calculate_mean,
    calculate_median,
    get_min_max,
    filter_by_period,
    filter_by_period_range,
    calculate_volatility,
    calculate_price_trend,
    calculate_price_statistics,
    days_since_most_recent_price,
    get_recommended_period
)

# Import de notifiers
from .notifiers import (
    DiscordEmbedBuilder,
    format_price,
    format_price_history,
    get_unique_prices
)

__version__ = "0.0.1"
__all__ = [
    # Models
    "Product",
    "Price",
    "PriceHistory",
    "DiscountResult",
    "HistoryDiscountResult",
    "DiscountInfo",
    "PriceTrend",
    # Price Comparison
    "PriceComparisonStatus",
    "PriceAction",
    "PriceAdditionStrategy",
    "PriceComparisonResult",
    # Parser
    "parse_price",
    # Discount functions
    "calculate_discount_percentage",
    "calculate_discount_absolute",
    "is_real_discount",
    "calculate_discount_from_history",
    "get_discount_info",
    "get_best_discount_from_history",
    # Statistics
    "calculate_mean",
    "calculate_median",
    "get_min_max",
    "filter_by_period",
    "filter_by_period_range",
    "calculate_volatility",
    "calculate_price_trend",
    "calculate_price_statistics",
    "days_since_most_recent_price",
    "get_recommended_period",
    # Notifiers (opcionais)
    "DiscordEmbedBuilder",
    "format_price",
    "format_price_history",
    "get_unique_prices",
]
