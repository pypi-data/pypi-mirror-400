"""
Test module for TradingContext

Test Categories:
1. TradingContextProxy - Struct field accessors
2. Static instances - base, advanced_entry, advanced_exit
3. Polars expressions - Returns pl.Expr for all properties
4. Backward compatibility - Aliases
"""


# TODO: Import from tradepose_client.builder
# from tradepose_client.builder import TradingContext, TradingContextProxy
# import polars as pl


class TestTradingContextProxy:
    """Test TradingContextProxy field accessors."""

    def test_entry_price_returns_expr(self):
        """Test entry_price returns pl.Expr."""
        # TODO: Arrange - proxy = TradingContextProxy()
        # TODO: Act - expr = proxy.entry_price
        # TODO: Assert - isinstance(expr, pl.Expr)
        # TODO: Assert - Access struct field "position_entry_price"
        pass

    def test_bars_in_position_returns_expr(self):
        """Test bars_in_position returns pl.Expr."""
        # TODO: Act - expr = proxy.bars_in_position
        # TODO: Assert - Access struct field "bars_in_position"
        pass

    def test_highest_since_entry_returns_expr(self):
        """Test highest_since_entry returns pl.Expr."""
        # TODO: Act - expr = proxy.highest_since_entry
        # TODO: Assert - Access struct field "highest_since_entry"
        pass

    def test_lowest_since_entry_returns_expr(self):
        """Test lowest_since_entry returns pl.Expr."""
        # TODO: Act - expr = proxy.lowest_since_entry
        # TODO: Assert - Access struct field "lowest_since_entry"
        pass


class TestTradingContextStaticInstances:
    """Test TradingContext static instances."""

    def test_base_context_exists(self):
        """Test TradingContext.base exists."""
        # TODO: Assert - hasattr(TradingContext, "base")
        # TODO: Assert - isinstance(TradingContext.base, TradingContextProxy)
        pass

    def test_advanced_entry_context_exists(self):
        """Test TradingContext.advanced_entry exists."""
        # TODO: Assert - hasattr(TradingContext, "advanced_entry")
        pass

    def test_advanced_exit_context_exists(self):
        """Test TradingContext.advanced_exit exists."""
        # TODO: Assert - hasattr(TradingContext, "advanced_exit")
        pass

    def test_context_instances_are_distinct(self):
        """Test contexts are different instances."""
        # TODO: Assert - TradingContext.base is not TradingContext.advanced_entry
        pass


class TestTradingContextBackwardCompatibility:
    """Test backward compatibility aliases."""

    def test_old_aliases_still_work(self):
        """Test that any old naming still works (if applicable)."""
        # TODO: If there are deprecated aliases, test they still work
        pass
