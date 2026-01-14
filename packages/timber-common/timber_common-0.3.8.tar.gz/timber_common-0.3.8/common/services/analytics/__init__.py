# timber/common/services/analytics/__init__.py
"""
Financial Analytics Package

Provides fundamental analysis capabilities that are ADDITIVE to data_processor.

data_processor handles: Technical indicators, returns, risk metrics, portfolio metrics
analytics handles: Fundamental ratios, growth metrics, valuation (from financial statements)

Main entry points for task configs:
- calculate_financial_ratios(income_stmt, balance_sheet, cash_flow)
- calculate_growth_metrics(income_stmt, balance_sheet)  
- calculate_valuation_metrics(income_stmt, balance_sheet, cash_flow, market_cap, ...)
"""

from .fundamental import (
    # Individual ratio functions
    calculate_profitability_ratios,
    calculate_leverage_ratios,
    calculate_liquidity_ratios,
    calculate_efficiency_ratios,
    calculate_cashflow_ratios,
    # Main umbrella function
    calculate_financial_ratios,
)

from .growth import (
    calculate_revenue_growth,
    calculate_earnings_growth,
    calculate_margin_trends,
    calculate_asset_growth,
    # Main umbrella function
    calculate_growth_metrics,
)

from .valuation import (
    calculate_price_multiples,
    calculate_ev_multiples,
    calculate_cf_valuation,
    calculate_peg_ratio,
    # Main umbrella function
    calculate_valuation_metrics,
)


# =============================================================================
# Unified Analytics Service Class
# =============================================================================

class FundamentalAnalytics:
    """
    Unified fundamental analytics service.
    
    Provides methods that can be called via Timber adapter:
        service: fundamental_analytics
        method: calculate_financial_ratios
    """
    
    # Fundamental Ratios
    @staticmethod
    def calculate_financial_ratios(income_stmt, balance_sheet, cash_flow=None, period_idx=0):
        """Calculate all fundamental ratios from financial statements."""
        return calculate_financial_ratios(income_stmt, balance_sheet, cash_flow, period_idx)
    
    @staticmethod
    def calculate_profitability_ratios(income_stmt, balance_sheet, period_idx=0):
        """Calculate profitability ratios."""
        return calculate_profitability_ratios(income_stmt, balance_sheet, period_idx)
    
    @staticmethod
    def calculate_leverage_ratios(balance_sheet, income_stmt=None, period_idx=0):
        """Calculate leverage/solvency ratios."""
        return calculate_leverage_ratios(balance_sheet, income_stmt, period_idx)
    
    @staticmethod
    def calculate_liquidity_ratios(balance_sheet, period_idx=0):
        """Calculate liquidity ratios."""
        return calculate_liquidity_ratios(balance_sheet, period_idx)
    
    @staticmethod
    def calculate_efficiency_ratios(income_stmt, balance_sheet, period_idx=0):
        """Calculate efficiency ratios."""
        return calculate_efficiency_ratios(income_stmt, balance_sheet, period_idx)
    
    @staticmethod
    def calculate_cashflow_ratios(cash_flow, income_stmt=None, balance_sheet=None, period_idx=0):
        """Calculate cash flow quality ratios."""
        return calculate_cashflow_ratios(cash_flow, income_stmt, balance_sheet, period_idx)
    
    # Growth Metrics
    @staticmethod
    def calculate_growth_metrics(income_stmt, balance_sheet=None):
        """Calculate all growth metrics."""
        return calculate_growth_metrics(income_stmt, balance_sheet)
    
    @staticmethod
    def calculate_revenue_growth(income_stmt):
        """Calculate revenue growth metrics."""
        return calculate_revenue_growth(income_stmt)
    
    @staticmethod
    def calculate_earnings_growth(income_stmt):
        """Calculate earnings growth metrics."""
        return calculate_earnings_growth(income_stmt)
    
    @staticmethod
    def calculate_margin_trends(income_stmt):
        """Calculate margin trends."""
        return calculate_margin_trends(income_stmt)
    
    @staticmethod
    def calculate_asset_growth(balance_sheet):
        """Calculate asset/equity growth."""
        return calculate_asset_growth(balance_sheet)
    
    # Valuation Metrics
    @staticmethod
    def calculate_valuation_metrics(
        income_stmt, balance_sheet, cash_flow=None,
        market_cap=None, current_price=None, shares_outstanding=None,
        period_idx=0
    ):
        """Calculate all valuation metrics."""
        return calculate_valuation_metrics(
            income_stmt, balance_sheet, cash_flow,
            market_cap, current_price, shares_outstanding,
            period_idx
        )
    
    @staticmethod
    def calculate_price_multiples(
        income_stmt, balance_sheet, market_cap,
        shares_outstanding=None, current_price=None, period_idx=0
    ):
        """Calculate P/E, P/B, P/S ratios."""
        return calculate_price_multiples(
            income_stmt, balance_sheet, market_cap,
            shares_outstanding, current_price, period_idx
        )
    
    @staticmethod
    def calculate_ev_multiples(income_stmt, balance_sheet, market_cap, period_idx=0):
        """Calculate EV/EBITDA, EV/Revenue."""
        return calculate_ev_multiples(income_stmt, balance_sheet, market_cap, period_idx)
    
    @staticmethod
    def calculate_peg_ratio(income_stmt, market_cap, period_idx=0):
        """Calculate PEG ratio."""
        return calculate_peg_ratio(income_stmt, market_cap, period_idx)


# Create singleton instance
fundamental_analytics = FundamentalAnalytics()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Main service object
    'fundamental_analytics',
    'FundamentalAnalytics',
    
    # Fundamental Ratios
    'calculate_financial_ratios',
    'calculate_profitability_ratios',
    'calculate_leverage_ratios',
    'calculate_liquidity_ratios',
    'calculate_efficiency_ratios',
    'calculate_cashflow_ratios',
    
    # Growth Metrics
    'calculate_growth_metrics',
    'calculate_revenue_growth',
    'calculate_earnings_growth',
    'calculate_margin_trends',
    'calculate_asset_growth',
    
    # Valuation Metrics
    'calculate_valuation_metrics',
    'calculate_price_multiples',
    'calculate_ev_multiples',
    'calculate_cf_valuation',
    'calculate_peg_ratio',
]
