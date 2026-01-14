"""
Modelos de dados para produtos e preços.
"""

from dataclasses import dataclass
from datetime import datetime
from itertools import product
from typing import List, Optional
from enum import Enum


class PriceComparisonStatus(Enum):
    """Status da comparação entre preços."""
    DECREASED = "decreased"    # Preço caiu
    INCREASED = "increased"    # Preço subiu
    EQUAL = "equal"           # Preço igual
    FIRST_PRICE = "first_price"  # Primeiro preço (histórico vazio)


class PriceAction(Enum):
    """Ação realizada ao adicionar preço."""
    ADDED = "added"           # Novo preço adicionado
    UPDATED = "updated"       # Preço existente atualizado (ex: data)
    REJECTED = "rejected"     # Não foi aceito
    NONE = "none"            # Nenhuma ação (apenas comparação)


class PriceAdditionStrategy(Enum):
    """Estratégia para adição de preços ao histórico."""
    ALWAYS = "always"                    # Sempre adiciona
    ONLY_DECREASE = "only_decrease"      # Só adiciona se preço caiu
    SMART = "smart"                      # Inteligente (default)
    UPDATE_ON_EQUAL = "update_on_equal"  # Atualiza data se preço igual


@dataclass
class Product:
    """
    Representa um produto com informações básicas.

    Attributes:
        product_id: Identificador único do produto
        name: Nome do produto
        url: URL do produto (opcional, para link no embed)
        image_url: URL da imagem do produto (opcional, para thumbnail)
    """
    product_id: str
    name: str
    url: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class Price:
    """
    Representa um preço em um determinado momento.

    Attributes:
        value: Valor do preço (sempre em formato decimal, ex: 1299.90)
        date: Data e hora do preço
        currency: Código da moeda (ex: "BRL", "USD")
        source: Fonte do preço (ex: "mercadolivre", "amazon")
    """
    value: float
    date: datetime
    currency: str = "BRL"
    source: Optional[str] = None

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Preço não pode ser negativo")
        if not isinstance(self.date, datetime):
            raise TypeError("date deve ser um objeto datetime")


@dataclass
class ProductWithCurrentPriceAndOldPrice:
    """
        Combina um produto com seu preço atual e antigo.
        Será usado usualmente para ser a entrada e conversões de API.
    """
    product: Product
    current_price: Price
    old_price: Optional[Price] = None


@dataclass
class ProductWithPriceHistory:
    """
    Combina um produto com seu histórico de preços.
    Usado para análises baseadas em histórico.

    Attributes:
        product: Objeto Product
        price_history: Objeto PriceHistory
    """
    product: Product
    price_history: 'PriceHistory'

@dataclass
class PriceHistory:
    """
    Representa o histórico de preços de um produto.

    Attributes:
        product_id: Identificador do produto
        prices: Lista de preços ordenada por data (mais recente primeiro)
    """
    product_id: str
    prices: List[Price]

    def __post_init__(self):
        # Cria cópia para não modificar a lista original do usuário
        self.prices = self.prices.copy()
        # Ordena preços por data (mais recente primeiro)
        self.prices.sort(key=lambda p: p.date, reverse=True)

    def get_current_price(self) -> Optional[Price]:
        """Retorna o preço mais recente."""
        return self.prices[0] if self.prices else None

    def get_previous_price(self) -> Optional[Price]:
        """Retorna o penúltimo preço."""
        return self.prices[1] if len(self.prices) > 1 else None

    def compare_price(
        self,
        new_price: 'Price',
        min_hours_for_increase: int = 24
    ) -> 'PriceComparisonResult':
        """
        Compara novo preço com histórico SEM modificar.

        Útil para análise antes de decidir se adiciona.
        Não altera self.prices.

        Args:
            new_price: Preço a ser comparado
            min_hours_for_increase: Horas mínimas para aceitar aumento

        Returns:
            PriceComparisonResult com action=NONE
        """
        current = self.get_current_price()

        # Caso 1: Histórico vazio
        if not current:
            return PriceComparisonResult(
                status=PriceComparisonStatus.FIRST_PRICE,
                current_price=None,
                new_price=new_price,
                value_difference=0.0,
                percentage_difference=0.0,
                time_difference_hours=None,
                should_add=True,
                reason="first price in history",
                action=PriceAction.NONE
            )

        # Calcular diferenças
        value_diff = new_price.value - current.value
        pct_diff = (value_diff / current.value) * 100 if current.value > 0 else 0.0
        time_diff = (new_price.date - current.date).total_seconds() / 3600  # horas

        # Determinar status
        if new_price.value < current.value:
            status = PriceComparisonStatus.DECREASED
            should_add = True
            reason = "price decreased"
        elif new_price.value > current.value:
            status = PriceComparisonStatus.INCREASED
            if time_diff >= min_hours_for_increase:
                should_add = True
                reason = f"price increased after {time_diff:.1f} hours"
            else:
                should_add = False
                reason = f"recent increase (only {time_diff:.1f} hours, need {min_hours_for_increase})"
        else:  # igual
            status = PriceComparisonStatus.EQUAL
            should_add = False
            reason = "price unchanged"

        return PriceComparisonResult(
            status=status,
            current_price=current,
            new_price=new_price,
            value_difference=round(value_diff, 2),
            percentage_difference=round(pct_diff, 2),
            time_difference_hours=round(time_diff, 2),
            should_add=should_add,
            reason=reason,
            action=PriceAction.NONE
        )

    def add_price(
        self,
        price: 'Price',
        strategy: 'PriceAdditionStrategy' = PriceAdditionStrategy.SMART,
        min_hours_for_increase: int = 24
    ) -> 'PriceComparisonResult':
        """
        Adiciona preço ao histórico baseado na estratégia.

        Args:
            price: Preço a adicionar
            strategy: Estratégia de adição (padrão: SMART)
            min_hours_for_increase: Horas mínimas para aceitar aumento

        Returns:
            PriceComparisonResult com action apropriada (ADDED, UPDATED, REJECTED)
        """
        # Primeiro compara
        result = self.compare_price(price, min_hours_for_increase)

        # Aplica estratégia
        if strategy == PriceAdditionStrategy.ALWAYS:
            # Sempre adiciona - cria nova lista
            new_prices = self.prices.copy()
            new_prices.append(price)
            new_prices.sort(key=lambda p: p.date, reverse=True)
            self.prices = new_prices
            result.action = PriceAction.ADDED
            result.affected_price = price
            result.reason = "always strategy"

        elif strategy == PriceAdditionStrategy.ONLY_DECREASE:
            # Só adiciona se caiu
            if result.status == PriceComparisonStatus.DECREASED or result.status == PriceComparisonStatus.FIRST_PRICE:
                new_prices = self.prices.copy()
                new_prices.append(price)
                new_prices.sort(key=lambda p: p.date, reverse=True)
                self.prices = new_prices
                result.action = PriceAction.ADDED
                result.affected_price = price
            else:
                result.action = PriceAction.REJECTED
                result.reason = "only_decrease strategy: price did not decrease"

        elif strategy == PriceAdditionStrategy.UPDATE_ON_EQUAL:
            # Se igual: atualiza data do último
            if result.status == PriceComparisonStatus.EQUAL:
                result.previous_price = self.prices[0]
                new_prices = self.prices.copy()
                new_prices[0] = price  # Substitui (atualiza data)
                self.prices = new_prices
                result.action = PriceAction.UPDATED
                result.affected_price = price
                result.reason = "price equal, date updated"
            elif result.should_add:
                new_prices = self.prices.copy()
                new_prices.append(price)
                new_prices.sort(key=lambda p: p.date, reverse=True)
                self.prices = new_prices
                result.action = PriceAction.ADDED
                result.affected_price = price
            else:
                result.action = PriceAction.REJECTED

        else:  # SMART (default)
            # Adiciona se should_add=True (queda ou aumento após tempo)
            if result.should_add:
                new_prices = self.prices.copy()
                new_prices.append(price)
                new_prices.sort(key=lambda p: p.date, reverse=True)
                self.prices = new_prices
                result.action = PriceAction.ADDED
                result.affected_price = price
            else:
                result.action = PriceAction.REJECTED

        return result

    def update_latest_price_date(self, new_date: datetime) -> bool:
        """
        Atualiza data do preço mais recente sem mudar valor.

        Útil quando preço está igual mas quer timestamp atualizado.

        Args:
            new_date: Nova data para o preço mais recente

        Returns:
            True se atualizado, False se histórico vazio
        """
        if not self.prices:
            return False

        # Cria novo Price com valor antigo e data nova
        old_price = self.prices[0]
        updated_price = Price(
            value=old_price.value,
            date=new_date,
            currency=old_price.currency,
            source=old_price.source
        )

        # Cria nova lista ao invés de modificar
        new_prices = self.prices.copy()
        new_prices[0] = updated_price
        self.prices = new_prices
        return True

    def get_prices_by_currency(self, currency: str) -> List[Price]:
        """Retorna apenas preços de uma determinada moeda."""
        return [p for p in self.prices if p.currency == currency]


@dataclass
class PriceComparisonResult:
    """
    Resultado completo da comparação de preços.

    Usado para:
    - Análise de mudança de preço
    - Decisão de adicionar ao histórico
    - Integração com banco de dados
    - Logging e notificações

    Attributes:
        status: Status da comparação (DECREASED, INCREASED, EQUAL, FIRST_PRICE)
        current_price: Preço atual no histórico (None se vazio)
        new_price: Novo preço sendo comparado
        value_difference: Diferença em valor absoluto (R$)
        percentage_difference: Diferença percentual (%)
        time_difference_hours: Horas desde último preço (None se histórico vazio)
        should_add: Sugestão se deve adicionar ao histórico
        reason: Motivo da decisão (ex: "price decreased", "recent increase")
        action: Ação realizada (ADDED, UPDATED, REJECTED, NONE)
        affected_price: Objeto Price afetado (para persistência no BD)
        previous_price: Estado anterior do preço (se action=UPDATED)
    """
    status: PriceComparisonStatus
    current_price: Optional['Price']
    new_price: 'Price'
    value_difference: float
    percentage_difference: float
    time_difference_hours: Optional[float]
    should_add: bool
    reason: str
    action: PriceAction
    affected_price: Optional['Price'] = None
    previous_price: Optional['Price'] = None

    def to_dict(self) -> dict:
        """Converte para dicionário (útil para logs/JSON)."""
        return {
            'status': self.status.value,
            'current_price_value': self.current_price.value if self.current_price else None,
            'new_price_value': self.new_price.value,
            'value_difference': self.value_difference,
            'percentage_difference': self.percentage_difference,
            'time_difference_hours': self.time_difference_hours,
            'should_add': self.should_add,
            'reason': self.reason,
            'action': self.action.value,
            'affected_price_value': self.affected_price.value if self.affected_price else None,
        }


@dataclass
class DiscountResult:
    """
    Resultado básico de cálculo de desconto.

    Attributes:
        current_price: Preço atual do produto
        reference_price: Preço de referência usado para comparação
        discount_percentage: Percentual de desconto (positivo = desconto, negativo = aumento)
        discount_absolute: Valor absoluto do desconto
        is_real_discount: Se o desconto é considerado real (percentual > 0)
    """
    current_price: float
    reference_price: float
    discount_percentage: float
    discount_absolute: float
    is_real_discount: bool

    def to_dict(self) -> dict:
        """Converte para dicionário (compatibilidade)."""
        return {
            'current_price': self.current_price,
            'reference_price': self.reference_price,
            'discount_percentage': self.discount_percentage,
            'discount_absolute': self.discount_absolute,
            'is_real_discount': self.is_real_discount
        }


@dataclass
class HistoryDiscountResult(DiscountResult):
    """
    Resultado de desconto calculado baseado em histórico de preços.

    Extends DiscountResult com informações sobre o cálculo histórico.

    Attributes:
        calculation_method: Método usado ('mean' ou 'median')
        period_days: Período em dias usado para cálculo (None = todos os preços)
        samples_count: Quantidade de amostras (preços) usadas no cálculo
    """
    calculation_method: str  # 'mean' ou 'median'
    period_days: Optional[int] = None
    samples_count: int = 0

    def to_dict(self) -> dict:
        """Converte para dicionário (compatibilidade)."""
        base = super().to_dict()
        base.update({
            'calculation_method': self.calculation_method,
            'period_days': self.period_days,
            'samples_count': self.samples_count
        })
        return base


@dataclass
class DiscountInfo:
    """
    Informações completas de desconto com estratégia de cálculo.

    Usado pela função get_discount_info() que escolhe automaticamente
    entre usar histórico ou preço anunciado.

    Attributes:
        current_price: Preço atual do produto
        reference_price: Preço de referência usado (média histórica ou advertised)
        discount_percentage: Percentual de desconto
        discount_absolute: Valor absoluto do desconto
        is_real_discount: Se o desconto é considerado real
        strategy: Estratégia usada ('history' ou 'advertised')
        has_history: Se havia histórico disponível
        calculation_method: Método de cálculo ('mean', 'median' ou 'advertised')
        period_days: Período usado (apenas se strategy='history')
        samples_count: Quantidade de amostras (apenas se strategy='history')
        adjusted_period_days: Período ajustado automaticamente (se auto_adjust_period=True)
        days_since_most_recent: Dias desde o preço mais recente até hoje
        skip_recent_days: Dias mais recentes ignorados (se > 0)
    """
    current_price: float
    reference_price: float
    discount_percentage: float
    discount_absolute: float
    is_real_discount: bool
    strategy: str  # 'history' ou 'advertised'
    has_history: bool
    calculation_method: str  # 'mean', 'median' ou 'advertised'
    period_days: Optional[int] = None
    samples_count: Optional[int] = None
    adjusted_period_days: Optional[int] = None
    days_since_most_recent: Optional[int] = None
    skip_recent_days: Optional[int] = None

    def to_dict(self) -> dict:
        """Converte para dicionário (compatibilidade)."""
        return {
            'current_price': self.current_price,
            'reference_price': self.reference_price,
            'discount_percentage': self.discount_percentage,
            'discount_absolute': self.discount_absolute,
            'is_real_discount': self.is_real_discount,
            'strategy': self.strategy,
            'has_history': self.has_history,
            'calculation_method': self.calculation_method,
            'period_days': self.period_days,
            'samples_count': self.samples_count,
            'adjusted_period_days': self.adjusted_period_days,
            'days_since_most_recent': self.days_since_most_recent,
            'skip_recent_days': self.skip_recent_days
        }


@dataclass
class PriceTrend:
    """
    Análise detalhada de tendência de preços ao longo do tempo.

    Compara períodos de tempo para detectar direção, magnitude e
    confiabilidade da tendência.

    Attributes:
        direction: Direção da tendência ('increasing', 'decreasing', 'stable')
        change_percentage: Percentual de mudança entre períodos (positivo = aumento)
        recent_avg: Preço médio do período recente
        previous_avg: Preço médio do período anterior
        volatility: Volatilidade (desvio padrão) dos preços
        confidence: Nível de confiança ('high', 'medium', 'low') baseado em amostras
        samples_recent: Quantidade de amostras do período recente
        samples_previous: Quantidade de amostras do período anterior
        is_accelerating: Se a tendência está acelerando (mudança > 10%)
        analysis_period_days: Período em dias usado para análise
    """
    direction: str  # 'increasing', 'decreasing', 'stable'
    change_percentage: float
    recent_avg: float
    previous_avg: float
    volatility: float
    confidence: str  # 'high', 'medium', 'low'
    samples_recent: int
    samples_previous: int
    is_accelerating: bool
    analysis_period_days: int

    def to_dict(self) -> dict:
        """Converte para dicionário (compatibilidade)."""
        return {
            'direction': self.direction,
            'change_percentage': self.change_percentage,
            'recent_avg': self.recent_avg,
            'previous_avg': self.previous_avg,
            'volatility': self.volatility,
            'confidence': self.confidence,
            'samples_recent': self.samples_recent,
            'samples_previous': self.samples_previous,
            'is_accelerating': self.is_accelerating,
            'analysis_period_days': self.analysis_period_days
        }

    def is_stable(self) -> bool:
        """Retorna True se a tendência é estável."""
        return self.direction == 'stable'

    def is_increasing(self) -> bool:
        """Retorna True se a tendência é de aumento."""
        return self.direction == 'increasing'

    def is_decreasing(self) -> bool:
        """Retorna True se a tendência é de queda."""
        return self.direction == 'decreasing'

    def has_high_confidence(self) -> bool:
        """Retorna True se a análise tem alta confiança."""
        return self.confidence == 'high'
