"""
策略构建器（主入口类）

管理整体策略构建流程：
1. 自动继承 base_instrument 和 base_freq
2. 添加指标（返回 IndicatorSpec）
3. 设置 base blueprint
4. 添加 advanced blueprints（链式）
5. 构建最终 StrategyConfig

Usage:
    from tradepose_client.builder import StrategyBuilder, BlueprintBuilder

    # 1. 创建 builder
    builder = StrategyBuilder(
        name="KOG_US100_15T_ST_21_3",
        base_instrument="US100.cash_M15_FTMO_FUTURE",
        base_freq="15min"
    )

    # 2. 添加指标（自动继承 instrument_id）
    from tradepose_models.enums import IndicatorType, Freq

    atr = builder.add_indicator(IndicatorType.ATR, period=21, freq=Freq.DAY_1, shift=1)
    st = builder.add_indicator(
        IndicatorType.SUPERTREND,
        multiplier=3.0,
        volatility_column=atr.display_name(),
        freq=Freq.DAY_1,
        shift=1
    )

    # 3. 创建并设置 base blueprint
    base_bp = BlueprintBuilder("base", "Long", "Trend")\
        .add_entry_trigger(...)\
        .add_exit_trigger(...)\
        .build()

    builder.set_base_blueprint(base_bp)

    # 4. 添加 advanced blueprints
    adv_bp = BlueprintBuilder("risk_mgmt", "Long", "Trend")\
        .add_exit_trigger(...)\
        .build()

    builder.add_advanced_blueprint(adv_bp)

    # 5. 构建最终策略
    strategy = builder.build(
        volatility_indicator=atr,
        note="US100 顺势策略"
    )

    # 6. 保存或注册
    strategy.save("strategy.json")
"""

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    import polars as pl
    from tradepose_models.enums import Freq, IndicatorType
    from tradepose_models.strategy import Blueprint, IndicatorSpec, StrategyConfig


class StrategyBuilder:
    """
    策略构建器（主入口类）

    管理整体策略构建流程，自动继承 base_instrument 和 base_freq。

    Attributes:
        name (str): 策略名称
        base_instrument (str): 基准商品
        base_freq (Freq): 基准频率

    Methods:
        add_indicator(indicator_type, **kwargs) -> IndicatorSpec:
            添加指标（自动继承 instrument_id）
        set_base_blueprint(blueprint) -> StrategyBuilder:
            设置 Base Blueprint
        add_advanced_blueprint(blueprint) -> StrategyBuilder:
            添加 Advanced Blueprint（链式）
        build(volatility_indicator, note) -> StrategyConfig:
            构建最终 StrategyConfig
    """

    def __init__(
        self,
        name: str,
        base_instrument: str,
        base_freq: str,
    ):
        """
        初始化策略构建器

        Args:
            name: 策略名称（唯一标识）
            base_instrument: 基准商品 ID（所有指标自动继承此值）
            base_freq: 基准频率（支持字符串，如 "15min", "1D"）

        Examples:
            >>> builder = StrategyBuilder(
            ...     name="KOG_US100_15T_ST_21_3",
            ...     base_instrument="US100.cash_M15_FTMO_FUTURE",
            ...     base_freq="15min"
            ... )
        """
        self.name = name
        self.base_instrument = base_instrument
        self.base_freq = base_freq  # 字符串形式，稍后转换

        self._indicators: List["IndicatorSpec"] = []
        self._base_blueprint: Optional["Blueprint"] = None
        self._advanced_blueprints: List["Blueprint"] = []

    def add_indicator(
        self,
        indicator_type: Union["IndicatorType", str],
        freq: Union["Freq", str],
        shift: int = 1,
        instrument: Optional[str] = None,
        instrument_id: Optional[str] = None,  # Deprecated
        **kwargs,
    ) -> "IndicatorSpec":
        """
        添加指标（支持可选 instrument 覆盖）

        Args:
            indicator_type: 指标类型（支持 IndicatorType enum 或字符串）
                - IndicatorType.ATR 或 "atr"
                - IndicatorType.SMA 或 "sma"
                - IndicatorType.SUPERTREND 或 "supertrend"
            freq: 指标频率（支持 Freq enum 或字符串）
                - Freq.DAY_1 或 "1D"
                - Freq.HOUR_1 或 "1h"
                - Freq.MIN_15 或 "15min"
            shift: 位移（默认 1，依赖指标通常使用 0）
            instrument: 商品名稱（默认 None，使用 base_instrument）
                - None: 使用 self.base_instrument（常见用法）
                - "OTHER_INSTRUMENT": 使用其他商品（跨商品引用）
            instrument_id: [DEPRECATED] 請使用 instrument 參數
            **kwargs: 指标参数（传递给 Indicator 工厂方法）

        Returns:
            IndicatorSpec: 指标规范，提供 .col()、.display_name() 和 struct accessor

        Examples:
            >>> # 基本用法
            >>> atr = builder.add_indicator(
            ...     IndicatorType.ATR,
            ...     period=21,
            ...     freq=Freq.DAY_1,
            ...     shift=1
            ... )
            >>>
            >>> # 依赖指标（SuperTrend 引用 ATR）
            >>> st = builder.add_indicator(
            ...     IndicatorType.SUPERTREND,
            ...     multiplier=3.0,
            ...     volatility_column=atr.display_name(),  # 引用依赖
            ...     freq=Freq.DAY_1,
            ...     shift=1
            ... )
            >>>
            >>> # 使用 struct accessor
            >>> mp = builder.add_indicator(IndicatorType.MARKET_PROFILE, ...)
            >>> vah = mp.market_profile.vah  # 直接存取 struct 欄位
        """
        from tradepose_models.enums import Freq, IndicatorType
        from tradepose_models.indicators import Indicator
        from tradepose_models.strategy import create_indicator_spec

        # Backward compatibility: support old instrument_id parameter
        if instrument_id is not None:
            import warnings

            warnings.warn(
                "Parameter 'instrument_id' is deprecated, use 'instrument' instead. "
                "This parameter will be removed in version 2.0.0.",
                DeprecationWarning,
                stacklevel=2,
            )
            if instrument is None:
                instrument = instrument_id

        # 转换 indicator_type 为字符串
        if isinstance(indicator_type, IndicatorType):
            indicator_type_str = indicator_type.value
        else:
            indicator_type_str = indicator_type

        # 动态调用 Indicator 工厂方法
        if not hasattr(Indicator, indicator_type_str):
            raise ValueError(
                f"Unknown indicator type: '{indicator_type_str}'. "
                f"Available: {', '.join([e.value for e in IndicatorType])}"
            )

        indicator_factory = getattr(Indicator, indicator_type_str)
        indicator_config = indicator_factory(**kwargs)

        # 转换 freq 字符串/enum 为 Freq enum
        freq_enum = Freq(freq) if isinstance(freq, str) else freq

        # 使用 instrument（如果提供），否则使用 base_instrument
        final_instrument = instrument if instrument is not None else self.base_instrument

        # 创建 IndicatorSpec
        spec = create_indicator_spec(
            freq=freq_enum,
            indicator=indicator_config,
            instrument=final_instrument,
            shift=shift,
        )

        self._indicators.append(spec)
        return spec

    def set_base_blueprint(self, blueprint: "Blueprint") -> "StrategyBuilder":
        """
        设置 Base Blueprint

        Args:
            blueprint: Base Blueprint 对象（通常由 BlueprintBuilder 创建）

        Returns:
            StrategyBuilder: 返回自身，支持链式调用

        Examples:
            >>> base_bp = BlueprintBuilder("base", "Long", "Trend")\
            ...     .add_entry_trigger(...)\
            ...     .add_exit_trigger(...)\
            ...     .build()
            >>>
            >>> builder.set_base_blueprint(base_bp)
        """
        self._base_blueprint = blueprint
        return self

    def add_advanced_blueprint(self, blueprint: "Blueprint") -> "StrategyBuilder":
        """
        添加 Advanced Blueprint（链式调用）

        Args:
            blueprint: Advanced Blueprint 对象（通常由 BlueprintBuilder 创建）

        Returns:
            StrategyBuilder: 返回自身，支持链式调用

        Examples:
            >>> adv_bp = BlueprintBuilder("risk_mgmt", "Long", "Trend")\
            ...     .add_exit_trigger(...)\
            ...     .build()
            >>>
            >>> builder.add_advanced_blueprint(adv_bp)
        """
        self._advanced_blueprints.append(blueprint)
        return self

    def build(
        self,
        volatility_indicator: Optional["pl.Expr"] = None,
        note: str = "",
    ) -> "StrategyConfig":
        """
        构建最终 StrategyConfig

        Args:
            volatility_indicator: 波動率欄位表達式（pl.Expr），如 pl.col("1D_ATR|14")
            note: 策略说明

        Returns:
            StrategyConfig: 完整的策略配置对象

        Raises:
            ValueError: 如果未设置 base_blueprint

        Examples:
            >>> strategy = builder.build(
            ...     volatility_indicator=atr.col(),
            ...     note="US100 顺势策略 - SuperTrend(21,3)"
            ... )
        """
        from tradepose_models.enums import Freq
        from tradepose_models.strategy import StrategyConfig

        if not self._base_blueprint:
            raise ValueError("Base blueprint is required. Use .set_base_blueprint() first.")

        # 转换 base_freq 为 Freq enum
        base_freq_enum = Freq(self.base_freq) if isinstance(self.base_freq, str) else self.base_freq

        return StrategyConfig(
            name=self.name,
            base_instrument=self.base_instrument,
            base_freq=base_freq_enum,
            volatility_indicator=volatility_indicator,
            indicators=self._indicators,
            base_blueprint=self._base_blueprint,
            advanced_blueprints=self._advanced_blueprints,
            note=note,
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"StrategyBuilder(name='{self.name}', "
            f"base_instrument='{self.base_instrument}', "
            f"base_freq='{self.base_freq}', "
            f"indicators={len(self._indicators)}, "
            f"advanced_blueprints={len(self._advanced_blueprints)})"
        )
