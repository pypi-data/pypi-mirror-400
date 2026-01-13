"""
Trading Context 固定字段访问器

基于 schema.py 中定义的 struct 字段，提供简洁的属性访问方式，
避免繁琐的 `.struct.field()` 调用。

Usage:
    from tradepose_client.builder import TradingContext
    import polars as pl

    # 简洁访问（返回 pl.Expr）
    entry_price = TradingContext.base.entry_price
    highest = TradingContext.advanced_entry.highest_since_entry
    bars = TradingContext.advanced_exit.bars_since_entry

    # 用于策略条件表达式
    condition = TradingContext.base.bars_in_position > 50
    stop_loss_price = TradingContext.advanced_entry.entry_price - pl.col("atr") * 2
"""

import polars as pl


class TradingContextProxy:
    """
    Trading Context 字段访问代理

    为 base_trading_context, advanced_entry_trading_context,
    advanced_exit_trading_context 提供统一的属性访问接口。

    Args:
        context_name: 上下文字段名称（如 "base_trading_context"）
        context_type: 上下文类型（"base" 或 "advanced"）
    """

    def __init__(
        self,
        context_name: str,
    ):
        self._context_name = context_name

    @property
    def entry_price(self) -> pl.Expr:
        """
        进场价格

        Returns:
            pl.Expr: Polars 表达式，可直接用于条件或价格计算
        """
        return pl.col(self._context_name).struct.field("position_entry_price")

    @property
    def bars_in_position(self) -> pl.Expr:
        """
        持仓 K 线数（仅适用于 base_trading_context）

        Returns:
            pl.Expr: Polars 表达式

        Note:
            - base_trading_context 使用 "bars_in_position"
            - advanced 使用 "bars_since_advanced_entry"（请用 .bars_since_entry）
        """
        return pl.col(self._context_name).struct.field("bars_in_position")

    @property
    def highest_since_entry(self) -> pl.Expr:
        """
        进场以来最高价

        Returns:
            pl.Expr: Polars 表达式，可用于 trailing stop 计算
        """
        return pl.col(self._context_name).struct.field("highest_since_entry")

    @property
    def lowest_since_entry(self) -> pl.Expr:
        """
        进场以来最低价

        Returns:
            pl.Expr: Polars 表达式，可用于 short position trailing stop 计算
        """
        return pl.col(self._context_name).struct.field("lowest_since_entry")


class TradingContext:
    """
    Trading Context 统一访问器

    提供三种 trading context 的属性访问：
    - base: base_trading_context
    - advanced_entry: advanced_entry_trading_context
    - advanced_exit: advanced_exit_trading_context

    Usage:
        # Base context（Base Blueprint 生成）
        TradingContext.base.entry_price
        TradingContext.base.bars_in_position
        TradingContext.base.highest_since_entry
        TradingContext.base.lowest_since_entry

        # Advanced Entry context（Advanced Entry Triggers 使用）
        TradingContext.advanced_entry.entry_price
        TradingContext.advanced_entry.bars_since_entry
        TradingContext.advanced_entry.highest_since_entry
        TradingContext.advanced_entry.lowest_since_entry

        # Advanced Exit context（Advanced Exit Triggers 使用）
        TradingContext.advanced_exit.entry_price
        TradingContext.advanced_exit.bars_since_entry
        TradingContext.advanced_exit.highest_since_entry
        TradingContext.advanced_exit.lowest_since_entry

    Examples:
        # Stop Loss（Long）
        stop_loss_price = (
            TradingContext.advanced_entry.entry_price -
            pl.col("atr") * 2
        )

        # Trailing Stop（Long）
        trailing_stop_price = (
            TradingContext.advanced_entry.highest_since_entry -
            pl.col("atr") * 2
        )

        # 持倉時間過濾
        timeout_condition = TradingContext.advanced_entry.bars_since_entry > 100
    """

    base = TradingContextProxy("base_trading_context")
    advanced_entry = TradingContextProxy("advanced_entry_trading_context")
    advanced_exit = TradingContextProxy("advanced_exit_trading_context")


# 向后兼容的别名
BaseContext = TradingContext.base
AdvancedEntryContext = TradingContext.advanced_entry
AdvancedExitContext = TradingContext.advanced_exit
