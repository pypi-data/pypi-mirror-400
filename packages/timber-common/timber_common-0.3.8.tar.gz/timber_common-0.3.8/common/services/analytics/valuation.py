# timber/common/services/analytics/valuation.py
"""
Valuation Metrics - Price-based Valuation Ratios

Calculates valuation ratios that combine price data with financial statements.
Requires both market data (price, shares, market cap) and fundamentals.

Categories:
- Price multiples: P/E, P/B, P/S, P/CF
- Enterprise value: EV/EBITDA, EV/Revenue
- Yield metrics: Earnings yield, dividend yield
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

from .fundamental import INCOME_FIELDS, BALANCE_FIELDS, CASHFLOW_FIELDS, _get_value, _safe_divide


# =============================================================================
# TYPE COERCION HELPER
# =============================================================================

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


# =============================================================================
# PRICE MULTIPLES
# =============================================================================

def calculate_price_multiples(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    market_cap: float,
    shares_outstanding: float = None,
    current_price: float = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate price-based valuation multiples.
    
    Args:
        income_stmt: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        market_cap: Current market capitalization
        shares_outstanding: Number of shares (optional, calculated from market_cap/price)
        current_price: Current stock price (optional)
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (multiples_dict, error_message)
    """
    try:
        # Coerce numeric inputs
        market_cap = _to_float(market_cap)
        shares_outstanding = _to_float(shares_outstanding)
        current_price = _to_float(current_price)
        period_idx = int(period_idx) if period_idx is not None else 0
        
        # Ensure valid DataFrames
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        # Calculate shares if not provided
        if shares_outstanding is None and current_price and current_price > 0:
            shares_outstanding = market_cap / current_price
        
        # Get financial data
        net_income = _get_value(income_stmt, INCOME_FIELDS['net_income'], period_idx)
        revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], period_idx)
        total_equity = _get_value(balance_sheet, BALANCE_FIELDS['total_equity'], period_idx)
        
        result = {
            'market_cap': market_cap,
            'shares_outstanding': shares_outstanding,
            'current_price': current_price,
        }
        
        # P/E Ratio = Market Cap / Net Income (or Price / EPS)
        result['pe_ratio'] = _safe_divide(market_cap, net_income)
        
        # P/B Ratio = Market Cap / Book Value (Total Equity)
        result['pb_ratio'] = _safe_divide(market_cap, total_equity)
        
        # P/S Ratio = Market Cap / Revenue
        result['ps_ratio'] = _safe_divide(market_cap, revenue)
        
        # Earnings Yield = Net Income / Market Cap (inverse of P/E)
        result['earnings_yield'] = _safe_divide(net_income, market_cap)
        
        # Per-share metrics if we have shares
        if shares_outstanding and shares_outstanding > 0:
            result['eps'] = _safe_divide(net_income, shares_outstanding)
            result['book_value_per_share'] = _safe_divide(total_equity, shares_outstanding)
            result['revenue_per_share'] = _safe_divide(revenue, shares_outstanding)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating price multiples: {e}")
        return {}, str(e)


# =============================================================================
# ENTERPRISE VALUE MULTIPLES
# =============================================================================

def calculate_ev_multiples(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    market_cap: float,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate Enterprise Value based multiples.
    
    EV = Market Cap + Total Debt - Cash
    
    Args:
        income_stmt: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        market_cap: Current market capitalization
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ev_multiples_dict, error_message)
    """
    try:
        # Coerce numeric inputs
        market_cap = _to_float(market_cap)
        period_idx = int(period_idx) if period_idx is not None else 0
        
        if market_cap is None:
            return {}, "market_cap is required"
        
        # Ensure valid DataFrames
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        # Get balance sheet items for EV calculation
        total_debt = _get_value(balance_sheet, BALANCE_FIELDS['total_debt'], period_idx)
        cash = _get_value(balance_sheet, BALANCE_FIELDS['cash'], period_idx)
        
        # Calculate Enterprise Value
        ev = market_cap + (total_debt or 0) - (cash or 0)
        
        # Get income statement items
        revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], period_idx)
        operating_income = _get_value(income_stmt, INCOME_FIELDS['operating_income'], period_idx)
        depreciation = _get_value(income_stmt, INCOME_FIELDS['depreciation'], period_idx)
        ebitda_reported = _get_value(income_stmt, INCOME_FIELDS['ebitda'], period_idx)
        
        # Calculate EBITDA if not directly available
        if ebitda_reported:
            ebitda = ebitda_reported
        elif operating_income is not None:
            ebitda = operating_income + (depreciation or 0)
        else:
            ebitda = None
        
        result = {
            'enterprise_value': ev,
            'total_debt': total_debt,
            'cash': cash,
            'ebitda': ebitda,
        }
        
        # EV/EBITDA
        result['ev_to_ebitda'] = _safe_divide(ev, ebitda)
        
        # EV/Revenue
        result['ev_to_revenue'] = _safe_divide(ev, revenue)
        
        # EV/EBIT
        result['ev_to_ebit'] = _safe_divide(ev, operating_income)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating EV multiples: {e}")
        return {}, str(e)


# =============================================================================
# CASH FLOW VALUATION
# =============================================================================

def calculate_cf_valuation(
    cash_flow: pd.DataFrame,
    market_cap: float,
    shares_outstanding: float = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate cash flow based valuation metrics.
    
    Args:
        cash_flow: Cash flow statement DataFrame
        market_cap: Current market capitalization
        shares_outstanding: Number of shares (optional)
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (cf_valuation_dict, error_message)
    """
    try:
        # Coerce numeric inputs
        market_cap = _to_float(market_cap)
        shares_outstanding = _to_float(shares_outstanding)
        period_idx = int(period_idx) if period_idx is not None else 0
        
        # Ensure valid DataFrame
        cash_flow = _ensure_dataframe(cash_flow)
        ocf = _get_value(cash_flow, CASHFLOW_FIELDS['operating_cash_flow'], period_idx)
        capex = _get_value(cash_flow, CASHFLOW_FIELDS['capital_expenditure'], period_idx)
        fcf = _get_value(cash_flow, CASHFLOW_FIELDS['free_cash_flow'], period_idx)
        
        # Calculate FCF if not directly available
        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf + capex  # capex is typically negative
        
        result = {
            'operating_cash_flow': ocf,
            'free_cash_flow': fcf,
        }
        
        # P/OCF = Market Cap / Operating Cash Flow
        result['price_to_ocf'] = _safe_divide(market_cap, ocf)
        
        # P/FCF = Market Cap / Free Cash Flow
        result['price_to_fcf'] = _safe_divide(market_cap, fcf)
        
        # FCF Yield = FCF / Market Cap
        result['fcf_yield'] = _safe_divide(fcf, market_cap)
        
        # Per-share FCF
        if shares_outstanding and shares_outstanding > 0:
            result['fcf_per_share'] = _safe_divide(fcf, shares_outstanding)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating CF valuation: {e}")
        return {}, str(e)


# =============================================================================
# PEG RATIO
# =============================================================================

def calculate_peg_ratio(
    income_stmt: pd.DataFrame,
    market_cap: float,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate PEG Ratio (P/E to Growth).
    
    PEG = P/E Ratio / Earnings Growth Rate
    
    Args:
        income_stmt: Income statement DataFrame
        market_cap: Current market capitalization
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (peg_dict, error_message)
    """
    try:
        # Coerce numeric inputs
        market_cap = _to_float(market_cap)
        period_idx = int(period_idx) if period_idx is not None else 0
        
        # Ensure valid DataFrame
        income_stmt = _ensure_dataframe(income_stmt)
        
        num_periods = len(income_stmt.columns) if not income_stmt.empty else 0
        
        # Get earnings for multiple periods
        net_income_current = _get_value(income_stmt, INCOME_FIELDS['net_income'], period_idx)
        net_income_previous = _get_value(income_stmt, INCOME_FIELDS['net_income'], period_idx + 1) if num_periods > 1 else None
        
        result = {}
        
        # P/E Ratio
        pe_ratio = _safe_divide(market_cap, net_income_current)
        result['pe_ratio'] = pe_ratio
        
        # Earnings Growth Rate
        if net_income_current and net_income_previous and net_income_previous > 0:
            earnings_growth = (net_income_current - net_income_previous) / abs(net_income_previous)
            result['earnings_growth'] = earnings_growth
            
            # PEG Ratio (only meaningful with positive growth)
            if pe_ratio and earnings_growth > 0:
                # Convert growth to percentage for standard PEG calculation
                result['peg_ratio'] = pe_ratio / (earnings_growth * 100)
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error calculating PEG ratio: {e}")
        return {}, str(e)


# =============================================================================
# UMBRELLA FUNCTION - Main Entry Point
# =============================================================================

def calculate_valuation_metrics(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cash_flow: pd.DataFrame = None,
    market_cap: float = None,
    current_price: float = None,
    shares_outstanding: float = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Calculate all valuation metrics.
    
    This is the main entry point called by task configs via:
        service: fundamental_analytics
        method: calculate_valuation_metrics
    
    Note: Requires market_cap to be provided. This can come from:
        - fetch_company_info()['marketCap']
        - current_price * shares_outstanding
    
    Args:
        income_stmt: Income statement DataFrame (yfinance format)
        balance_sheet: Balance sheet DataFrame
        cash_flow: Cash flow statement DataFrame (optional)
        market_cap: Current market capitalization (required)
        current_price: Current stock price (optional)
        shares_outstanding: Number of shares (optional)
        period_idx: Which period to analyze (0=most recent)
    
    Returns:
        Tuple of (result_dict, error_string or None)
    """
    try:
        # Coerce numeric inputs from strings if needed
        market_cap = _to_float(market_cap)
        current_price = _to_float(current_price)
        shares_outstanding = _to_float(shares_outstanding)
        period_idx = int(period_idx) if period_idx is not None else 0
        
        # Ensure valid DataFrames
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        cash_flow = _ensure_dataframe(cash_flow)
        
        if market_cap is None or market_cap <= 0:
            # Return partial result instead of error - allows workflow to continue
            return {
                'success': False,
                'error': 'market_cap unavailable or invalid',
                'calculated_at': datetime.now(timezone.utc).isoformat(),
                'inputs': {
                    'market_cap': market_cap,
                    'current_price': current_price,
                    'shares_outstanding': shares_outstanding,
                },
                'price_multiples': {},
                'ev_multiples': {},
                'cash_flow_valuation': {},
                'peg': {},
            }, None  # No error string - allows workflow to continue
        
        result = {
            'success': True,
            'calculated_at': datetime.now(timezone.utc).isoformat(),
            'inputs': {
                'market_cap': market_cap,
                'current_price': current_price,
                'shares_outstanding': shares_outstanding,
                'period_idx': period_idx,
            },
            'errors': {},
        }
        
        # Price multiples
        price_multiples, err = calculate_price_multiples(
            income_stmt, balance_sheet, market_cap, 
            shares_outstanding, current_price, period_idx
        )
        if err:
            result['errors']['price_multiples'] = err
        result['price_multiples'] = price_multiples
        
        # EV multiples
        ev_multiples, err = calculate_ev_multiples(
            income_stmt, balance_sheet, market_cap, period_idx
        )
        if err:
            result['errors']['ev_multiples'] = err
        result['ev_multiples'] = ev_multiples
        
        # Cash flow valuation
        if cash_flow is not None and not cash_flow.empty:
            cf_valuation, err = calculate_cf_valuation(
                cash_flow, market_cap, shares_outstanding, period_idx
            )
            if err:
                result['errors']['cash_flow'] = err
            result['cash_flow_valuation'] = cf_valuation
        
        # PEG ratio
        peg, err = calculate_peg_ratio(income_stmt, market_cap, period_idx)
        if err:
            result['errors']['peg'] = err
        result['peg'] = peg
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error in calculate_valuation_metrics: {e}")
        return {'success': False, 'error': str(e)}, str(e)