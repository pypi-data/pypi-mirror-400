# timber/common/services/analytics/growth.py
"""
Growth Metrics - Period-over-Period Analysis

Calculates growth rates from financial statements using multiple periods.
Works with yfinance format: rows=line items, cols=dates (most recent first)

Categories:
- Revenue growth (QoQ, YoY)
- Earnings growth
- CAGR (Compound Annual Growth Rate)
- Margin trends
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Reuse field mappings from fundamental
from .fundamental import INCOME_FIELDS, BALANCE_FIELDS, _get_value, _safe_divide


def _to_int(value, default: int = 0) -> int:
    """Safely convert value to int, handling strings and None."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _to_float(value) -> Optional[float]:
    """Safely convert value to float, handling strings and None."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _ensure_dataframe(df) -> pd.DataFrame:
    """Ensure we have a valid DataFrame, return empty if not."""
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    return df


def _calculate_growth_rate(
    current: Optional[float],
    previous: Optional[float]
) -> Optional[float]:
    """Calculate period-over-period growth rate."""
    if current is None or previous is None or previous == 0:
        return None
    return (current - previous) / abs(previous)


def _calculate_cagr(
    ending: Optional[float],
    beginning: Optional[float],
    periods: int
) -> Optional[float]:
    """
    Calculate Compound Annual Growth Rate.
    
    CAGR = (ending/beginning)^(1/periods) - 1
    """
    if ending is None or beginning is None or beginning <= 0 or periods <= 0:
        return None
    if ending <= 0:
        return None
    return (ending / beginning) ** (1 / periods) - 1


# =============================================================================
# REVENUE GROWTH
# =============================================================================

def calculate_revenue_growth(
    income_stmt: pd.DataFrame,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate revenue growth metrics across periods.
    
    Args:
        income_stmt: Income statement DataFrame (yfinance format)
    
    Returns:
        Tuple of (growth_dict, error_message)
    """
    try:
        income_stmt = _ensure_dataframe(income_stmt)
        num_periods = len(income_stmt.columns) if not income_stmt.empty else 0
        
        result = {
            'periods_available': num_periods,
        }
        
        # Get revenue for each period
        revenues = []
        for i in range(min(num_periods, 5)):  # Max 5 periods
            rev = _get_value(income_stmt, INCOME_FIELDS['revenue'], i)
            revenues.append(rev)
        
        # Most recent growth (QoQ or YoY depending on data)
        if len(revenues) >= 2:
            result['latest_growth'] = _calculate_growth_rate(revenues[0], revenues[1])
        
        # Two-period growth
        if len(revenues) >= 3:
            result['two_period_growth'] = _calculate_growth_rate(revenues[0], revenues[2])
        
        # CAGR over available periods
        if len(revenues) >= 2 and revenues[0] and revenues[-1]:
            result['cagr'] = _calculate_cagr(revenues[0], revenues[-1], len(revenues) - 1)
        
        # Average growth rate
        growth_rates = []
        for i in range(len(revenues) - 1):
            gr = _calculate_growth_rate(revenues[i], revenues[i + 1])
            if gr is not None:
                growth_rates.append(gr)
        
        if growth_rates:
            result['average_growth'] = sum(growth_rates) / len(growth_rates)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating revenue growth: {e}")
        return {}, str(e)


# =============================================================================
# EARNINGS GROWTH
# =============================================================================

def calculate_earnings_growth(
    income_stmt: pd.DataFrame,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate earnings (net income) growth metrics.
    
    Args:
        income_stmt: Income statement DataFrame
    
    Returns:
        Tuple of (growth_dict, error_message)
    """
    try:
        income_stmt = _ensure_dataframe(income_stmt)
        num_periods = len(income_stmt.columns) if not income_stmt.empty else 0
        
        result = {
            'periods_available': num_periods,
        }
        
        # Get net income for each period
        earnings = []
        for i in range(min(num_periods, 5)):
            ni = _get_value(income_stmt, INCOME_FIELDS['net_income'], i)
            earnings.append(ni)
        
        # Most recent growth
        if len(earnings) >= 2:
            result['latest_growth'] = _calculate_growth_rate(earnings[0], earnings[1])
        
        # CAGR (only if both positive)
        if len(earnings) >= 2 and earnings[0] and earnings[-1]:
            if earnings[0] > 0 and earnings[-1] > 0:
                result['cagr'] = _calculate_cagr(earnings[0], earnings[-1], len(earnings) - 1)
        
        # Operating income growth
        op_incomes = []
        for i in range(min(num_periods, 5)):
            oi = _get_value(income_stmt, INCOME_FIELDS['operating_income'], i)
            op_incomes.append(oi)
        
        if len(op_incomes) >= 2:
            result['operating_income_growth'] = _calculate_growth_rate(op_incomes[0], op_incomes[1])
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating earnings growth: {e}")
        return {}, str(e)


# =============================================================================
# MARGIN TRENDS
# =============================================================================

def calculate_margin_trends(
    income_stmt: pd.DataFrame,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Calculate margin trends across periods.
    
    Args:
        income_stmt: Income statement DataFrame
    
    Returns:
        Tuple of (trends_dict, error_message)
    """
    try:
        income_stmt = _ensure_dataframe(income_stmt)
        num_periods = len(income_stmt.columns) if not income_stmt.empty else 0
        
        result = {
            'periods_available': num_periods,
            'gross_margins': [],
            'operating_margins': [],
            'net_margins': [],
        }
        
        for i in range(min(num_periods, 5)):
            revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], i)
            gross = _get_value(income_stmt, INCOME_FIELDS['gross_profit'], i)
            operating = _get_value(income_stmt, INCOME_FIELDS['operating_income'], i)
            net = _get_value(income_stmt, INCOME_FIELDS['net_income'], i)
            
            result['gross_margins'].append(_safe_divide(gross, revenue))
            result['operating_margins'].append(_safe_divide(operating, revenue))
            result['net_margins'].append(_safe_divide(net, revenue))
        
        # Calculate margin expansion/contraction
        if len(result['gross_margins']) >= 2:
            gm = result['gross_margins']
            if gm[0] is not None and gm[1] is not None:
                result['gross_margin_change'] = gm[0] - gm[1]
        
        if len(result['operating_margins']) >= 2:
            om = result['operating_margins']
            if om[0] is not None and om[1] is not None:
                result['operating_margin_change'] = om[0] - om[1]
        
        if len(result['net_margins']) >= 2:
            nm = result['net_margins']
            if nm[0] is not None and nm[1] is not None:
                result['net_margin_change'] = nm[0] - nm[1]
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating margin trends: {e}")
        return {}, str(e)


# =============================================================================
# ASSET GROWTH
# =============================================================================

def calculate_asset_growth(
    balance_sheet: pd.DataFrame,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate asset and equity growth metrics.
    
    Args:
        balance_sheet: Balance sheet DataFrame
    
    Returns:
        Tuple of (growth_dict, error_message)
    """
    try:
        balance_sheet = _ensure_dataframe(balance_sheet)
        num_periods = len(balance_sheet.columns) if not balance_sheet.empty else 0
        
        result = {
            'periods_available': num_periods,
        }
        
        # Total assets growth
        assets = []
        for i in range(min(num_periods, 5)):
            a = _get_value(balance_sheet, BALANCE_FIELDS['total_assets'], i)
            assets.append(a)
        
        if len(assets) >= 2:
            result['asset_growth'] = _calculate_growth_rate(assets[0], assets[1])
        
        # Equity growth
        equity = []
        for i in range(min(num_periods, 5)):
            e = _get_value(balance_sheet, BALANCE_FIELDS['total_equity'], i)
            equity.append(e)
        
        if len(equity) >= 2:
            result['equity_growth'] = _calculate_growth_rate(equity[0], equity[1])
        
        # Book value CAGR
        if len(equity) >= 2 and equity[0] and equity[-1] and equity[0] > 0 and equity[-1] > 0:
            result['book_value_cagr'] = _calculate_cagr(equity[0], equity[-1], len(equity) - 1)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating asset growth: {e}")
        return {}, str(e)


# =============================================================================
# UMBRELLA FUNCTION - Main Entry Point
# =============================================================================

def calculate_growth_metrics(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame = None,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Calculate all growth metrics from financial statements.
    
    This is the main entry point called by task configs via:
        service: fundamental_analytics
        method: calculate_growth_metrics
    
    Args:
        income_stmt: Income statement DataFrame (yfinance format)
        balance_sheet: Balance sheet DataFrame (optional)
    
    Returns:
        Tuple of (result_dict, error_string or None)
    """
    try:
        # Ensure valid DataFrames
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        
        result = {
            'success': True,
            'calculated_at': datetime.now(timezone.utc).isoformat(),
            'errors': {},
        }
        
        # Revenue growth
        revenue_growth, err = calculate_revenue_growth(income_stmt)
        if err:
            result['errors']['revenue'] = err
        result['revenue'] = revenue_growth
        
        # Earnings growth
        earnings_growth, err = calculate_earnings_growth(income_stmt)
        if err:
            result['errors']['earnings'] = err
        result['earnings'] = earnings_growth
        
        # Margin trends
        margin_trends, err = calculate_margin_trends(income_stmt)
        if err:
            result['errors']['margins'] = err
        result['margins'] = margin_trends
        
        # Asset growth (if balance sheet provided and not empty)
        if not balance_sheet.empty:
            asset_growth, err = calculate_asset_growth(balance_sheet)
            if err:
                result['errors']['assets'] = err
            result['assets'] = asset_growth
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error in calculate_growth_metrics: {e}")
        return {'success': False, 'error': str(e)}, str(e)