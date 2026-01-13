"""
Blueprint 链式构建器

支持链式添加 entry/exit triggers，最后通过 .build() 返回 BlueprintConfig。

Usage:
    from tradepose_client.builder import BlueprintBuilder, TradingContext
    import polars as pl

    # 创建 Base Blueprint
    base_bp = BlueprintBuilder(
        name="base_trend",
        direction="Long",
        trend_type="Trend",
        note="基础趋势策略"
    ).add_entry_trigger(
        name="entry",
        conditions=[pl.col("ema_20") > pl.col("ema_50")],
        price_expr=pl.col("open"),
        order_strategy="ImmediateEntry",
        priority=1,
        note="EMA 金叉"
    ).add_exit_trigger(
        name="exit",
        conditions=[pl.col("ema_20") < pl.col("ema_50")],
        price_expr=pl.col("open"),
        order_strategy="ImmediateExit",
        priority=1,
        note="EMA 死叉"
    ).build()

    # 创建 Advanced Blueprint
    adv_bp = BlueprintBuilder("risk_mgmt", "Long", "Trend")\
        .add_exit_trigger(
            name="stop_loss",
            conditions=[],
            price_expr=TradingContext.advanced_entry.entry_price - pl.col("atr") * 2,
            order_strategy="StopLoss",
            priority=1
        )\
        .add_exit_trigger(
            name="take_profit",
            conditions=[],
            price_expr=TradingContext.advanced_entry.entry_price + pl.col("atr") * 3,
            order_strategy="TakeProfit",
            priority=2
        )\
        .build()
"""

from typing import TYPE_CHECKING, List, Union

import polars as pl

if TYPE_CHECKING:
    from tradepose_models.enums import OrderStrategy, TradeDirection, TrendType
    from tradepose_models.strategy import Blueprint, Trigger


class BlueprintBuilder:
    """
    Blueprint 链式构建器

    支持链式添加 entry/exit triggers，提供流畅的 API 体验。

    Attributes:
        name (str): Blueprint 名称
        direction (str): 交易方向（"Long", "Short", "Both"）
        trend_type (str): 趋势类型（"Trend", "Range", "Reversal"）
        entry_first (bool): 是否必须先进场才能出场
        note (str): 备注

    Methods:
        add_entry_trigger(...) -> BlueprintBuilder: 添加进场触发器（链式）
        add_exit_trigger(...) -> BlueprintBuilder: 添加出场触发器（链式）
        build() -> Blueprint: 构建最终 Blueprint 对象
    """

    def __init__(
        self,
        name: str,
        direction: Union["TradeDirection", str],
        trend_type: Union["TrendType", str] = "Trend",
        entry_first: bool = True,
        note: str = "",
    ):
        """
        初始化 Blueprint 构建器

        Args:
            name: Blueprint 名称（唯一标识）
            direction: 交易方向
                - "Long": 做多
                - "Short": 做空
                - "Both": 双向（暂不支持）
            trend_type: 趋势类型
                - "Trend": 趋势跟随
                - "Range": 区间震荡
                - "Reversal": 反转交易
            entry_first: 是否必须先进场才能出场（推荐 True）
            note: Blueprint 说明

        Examples:
            >>> # Base Blueprint（简洁形式）
            >>> bp = BlueprintBuilder("base", "Long", "Trend")
            >>>
            >>> # Advanced Blueprint（完整形式）
            >>> adv_bp = BlueprintBuilder(
            ...     name="risk_management",
            ...     direction="Long",
            ...     trend_type="Trend",
            ...     entry_first=True,
            ...     note="Stop Loss + Take Profit"
            ... )
        """
        self.name = name
        self.direction = direction
        self.trend_type = trend_type
        self.entry_first = entry_first
        self.note = note

        self._entry_triggers: List["Trigger"] = []
        self._exit_triggers: List["Trigger"] = []

    def add_entry_trigger(
        self,
        name: str,
        conditions: List[pl.Expr],
        price_expr: pl.Expr,
        order_strategy: Union["OrderStrategy", str],
        priority: int,
        note: str = "",
    ) -> "BlueprintBuilder":
        """
        添加进场触发器（链式调用）

        Args:
            name: 触发器名称（唯一标识）
            conditions: 条件表达式列表（全部为 True 才触发）
            price_expr: 价格表达式（Polars Expr）
            order_strategy: 订单策略
                - Base Blueprint 必须使用 "ImmediateEntry"
                - Advanced Blueprint 可使用 "FavorableDelayEntry", "AdverseDelayEntry" 等
            priority: 优先级（1-100，越小优先级越高）
            note: 触发器说明

        Returns:
            BlueprintBuilder: 返回自身，支持链式调用

        Examples:
            >>> bp = BlueprintBuilder("base", "Long", "Trend")\
            ...     .add_entry_trigger(
            ...         name="entry",
            ...         conditions=[pl.col("ema_20") > pl.col("ema_50")],
            ...         price_expr=pl.col("open"),
            ...         order_strategy="ImmediateEntry",
            ...         priority=1,
            ...         note="EMA 金叉"
            ...     )
        """
        from tradepose_models.strategy import create_trigger

        trigger = create_trigger(
            name=name,
            conditions=conditions,
            price_expr=price_expr,
            order_strategy=order_strategy,
            priority=priority,
            note=note,
        )
        self._entry_triggers.append(trigger)
        return self

    def add_exit_trigger(
        self,
        name: str,
        conditions: List[pl.Expr],
        price_expr: pl.Expr,
        order_strategy: Union["OrderStrategy", str],
        priority: int,
        note: str = "",
    ) -> "BlueprintBuilder":
        """
        添加出场触发器（链式调用）

        Args:
            name: 触发器名称（唯一标识）
            conditions: 条件表达式列表（全部为 True 才触发）
            price_expr: 价格表达式（Polars Expr）
            order_strategy: 订单策略
                - Base Blueprint 必须使用 "ImmediateExit"
                - Advanced Blueprint 可使用 "StopLoss", "TakeProfit", "TrailingStop",
                  "Breakeven", "TimeoutExit" 等
            priority: 优先级（1-100，越小优先级越高）
            note: 触发器说明

        Returns:
            BlueprintBuilder: 返回自身，支持链式调用

        Examples:
            >>> bp = BlueprintBuilder("risk_mgmt", "Long", "Trend")\
            ...     .add_exit_trigger(
            ...         name="stop_loss",
            ...         conditions=[],
            ...         price_expr=TradingContext.advanced_entry.entry_price - pl.col("atr") * 2,
            ...         order_strategy="StopLoss",
            ...         priority=1,
            ...         note="固定止损 2 ATR"
            ...     )\
            ...     .add_exit_trigger(
            ...         name="take_profit",
            ...         conditions=[],
            ...         price_expr=TradingContext.advanced_entry.entry_price + pl.col("atr") * 3,
            ...         order_strategy="TakeProfit",
            ...         priority=2,
            ...         note="目标止盈 3 ATR"
            ...     )
        """
        from tradepose_models.strategy import create_trigger

        trigger = create_trigger(
            name=name,
            conditions=conditions,
            price_expr=price_expr,
            order_strategy=order_strategy,
            priority=priority,
            note=note,
        )
        self._exit_triggers.append(trigger)
        return self

    def build(self) -> "Blueprint":
        """
        构建最终 Blueprint 对象

        Returns:
            Blueprint: 完整的 Blueprint 配置对象

        Raises:
            ValueError: 如果未添加任何 trigger

        Examples:
            >>> bp = BlueprintBuilder("base", "Long", "Trend")\
            ...     .add_entry_trigger(...)\
            ...     .add_exit_trigger(...)\
            ...     .build()
            >>>
            >>> # 用于 StrategyBuilder
            >>> builder.set_base_blueprint(bp)
            >>> builder.add_advanced_blueprint(adv_bp)
        """
        from tradepose_models.strategy import create_blueprint

        if not self._entry_triggers and not self._exit_triggers:
            raise ValueError(
                f"Blueprint '{self.name}' must have at least one entry or exit trigger. "
                f"Use .add_entry_trigger() or .add_exit_trigger() before calling .build()"
            )

        return create_blueprint(
            name=self.name,
            direction=self.direction,
            entry_triggers=self._entry_triggers,
            exit_triggers=self._exit_triggers,
            trend_type=self.trend_type,
            entry_first=self.entry_first,
            note=self.note,
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"BlueprintBuilder(name='{self.name}', "
            f"direction='{self.direction}', "
            f"entry_triggers={len(self._entry_triggers)}, "
            f"exit_triggers={len(self._exit_triggers)})"
        )
