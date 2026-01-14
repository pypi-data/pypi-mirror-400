"""
Notificador para Discord usando webhooks.
"""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

try:
    from discord_webhook import DiscordWebhook, DiscordEmbed
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    if TYPE_CHECKING:
        from discord_webhook import DiscordEmbed

from ..models import Product, Price, DiscountInfo
from .formatters import format_price, format_price_history


class DiscordEmbedBuilder:

    def build_embed(
        self,
        product: Product,
        discount_info: DiscountInfo,
        price_history: List[Price]
    ) -> "DiscordEmbed":
        """
        Constrói o embed Discord com informações do alerta.

        Args:
            product: Produto
            discount_info: Informações de desconto
            price_history: Histórico de preços

        Returns:
            DiscordEmbed configurado
        """
        # Título
        title = f"{discount_info.discount_percentage:.2f}% - {product.name}"

        # Cor baseada no desconto
        color = self._get_embed_color(discount_info.discount_percentage)

        # Cria embed
        embed = DiscordEmbed(
            title=title,
            # color=color
        )

        # Adiciona URL se disponível
        if product.url:
            embed.url = product.url

        # Campo: Preço Atual
        embed.add_embed_field(
            name="Preco Atual",
            value=format_price(discount_info.current_price),
            inline=True
        )

        # Campo: Preço de Referência
        ref_label = "mediana" if discount_info.strategy == "history" else "preco de"
        embed.add_embed_field(
            name="Preco de Referencia",
            value=f"{format_price(discount_info.reference_price)} ({ref_label})",
            inline=True
        )

        # Campo: Desconto (R$)
        embed.add_embed_field(
            name="Desconto (R$)",
            value=format_price(abs(discount_info.discount_absolute)),
            inline=True
        )

        # Campo: Desconto (%)
        embed.add_embed_field(
            name="Desconto (%)",
            value=f"{discount_info.discount_percentage:.2f}%",
            inline=True
        )

        # Campo: Histórico (últimos 5)
        embed.add_embed_field(
            name="Historico (ultimos 5)",
            value=format_price_history(price_history, limit=5),
            inline=False
        )

        # Thumbnail (imagem do produto)
        if product.image_url:
            embed.set_thumbnail(url=product.image_url)

        # Footer com data/hora
        # embed.set_footer(text=f"Notificacao gerada em {datetime.now().strftime('%d/%m/%Y as %H:%M')}")

        # Timestamp
        embed.set_timestamp()

        return embed

    def _get_embed_color(self, discount_percentage: float) -> int:
        """
        Retorna cor do embed baseado no percentual de desconto.

        Args:
            discount_percentage: Percentual de desconto (positivo = desconto, negativo = aumento)

        Returns:
            Cor em formato hexadecimal (int)
        """
        if discount_percentage >= 20.0:
            # Verde: desconto >= 20%
            return 0x00FF00
        elif discount_percentage >= 10.0:
            # Amarelo: desconto entre 10-19%
            return 0xFFFF00
        elif discount_percentage >= 1.0:
            # Azul: desconto entre 1-9%
            return 0x0099FF
        elif discount_percentage < 0:
            # Vermelho: aumento de preço
            return 0xFF0000
        else:
            # Cinza: estável (< 1%)
            return 0x808080
