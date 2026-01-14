# timber/common/services/analytics/fundamental.py
"""
Fundamental Analysis - Financial Statement Ratios

Calculates ratios from income statement, balance sheet, and cash flow DataFrames.
Works with yfinance format: rows=line items, cols=dates

These are ADDITIVE to data_processor which handles price-based technical analysis.

Categories:
- Profitability: ROE, ROA, ROIC, margins
- Leverage: Debt ratios, interest coverage
- Liquidity: Current ratio, quick ratio
- Efficiency: Asset turnover, inventory turnover
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# FIELD NAME MAPPINGS (handles yfinance naming variations)
# =============================================================================

INCOME_FIELDS = {
    'revenue': ['Total Revenue', 'Revenue', 'Revenues', 'Sales'],
    'gross_profit': ['Gross Profit'],
    'operating_income': ['Operating Income', 'EBIT'],
    'net_income': ['Net Income', 'Net Income Common Stockholders', 'Net Income From Continuing Operations'],
    'ebitda': ['EBITDA', 'Normalized EBITDA'],
    'interest_expense': ['Interest Expense', 'Interest Expense Non Operating'],
    'cost_of_revenue': ['Cost Of Revenue', 'Cost of Goods Sold'],
    'depreciation': ['Depreciation And Amortization', 'Reconciled Depreciation'],
}

BALANCE_FIELDS = {
    'total_assets': ['Total Assets'],
    'total_liabilities': ['Total Liabilities Net Minority Interest', 'Total Liabilities'],
    'total_equity': ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity'],
    'current_assets': ['Current Assets', 'Total Current Assets'],
    'current_liabilities': ['Current Liabilities', 'Total Current Liabilities'],
    'total_debt': ['Total Debt'],
    'long_term_debt': ['Long Term Debt', 'Long Term Debt And Capital Lease Obligation'],
    'short_term_debt': ['Current Debt', 'Current Debt And Capital Lease Obligation'],
    'cash': ['Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments'],
    'inventory': ['Inventory'],
    'receivables': ['Accounts Receivable', 'Net Receivables', 'Receivables'],
    'payables': ['Accounts Payable', 'Payables And Accrued Expenses'],
}

CASHFLOW_FIELDS = {
    'operating_cash_flow': ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'],
    'capital_expenditure': ['Capital Expenditure', 'Purchase Of Property Plant And Equipment'],
    'free_cash_flow': ['Free Cash Flow'],
    'dividends_paid': ['Cash Dividends Paid', 'Common Stock Dividend Paid', 'Payment Of Dividends'],
}


# =============================================================================
# VALUE EXTRACTION (yfinance format: rows=items, cols=dates)
# =============================================================================

def _get_value(df: pd.DataFrame, field_names: List[str], period_idx: int = 0) -> Optional[float]:
    """
    Extract value from yfinance-format DataFrame.
    
    Args:
        df: Financial statement (rows=line items, cols=dates)
        field_names: Possible row names for the field
        period_idx: Column index (0=most recent)
    
    Returns:
        Float value or None
    """
    if df is None or df.empty:
        return None
    
    for name in field_names:
        if name in df.index:
            try:
                val = df.loc[name].iloc[period_idx]
                if pd.notna(val):
                    return float(val)
            except (IndexError, KeyError):
                continue
    return None


def _safe_divide(num: Optional[float], denom: Optional[float]) -> Optional[float]:
    """Safely divide, returning None if invalid."""
    if num is None or denom is None or denom == 0:
        return None
    return num / denom


# =============================================================================
# PROFITABILITY RATIOS
# =============================================================================

def _to_int(value, default: int = 0) -> int:
    """Safely convert value to int, handling strings and None."""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _ensure_dataframe(df) -> pd.DataFrame:
    """Ensure we have a valid DataFrame, return empty if not."""
    if df is None:
        return pd.DataFrame()
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    return df


def calculate_profitability_ratios(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate profitability ratios from financial statements.
    
    Args:
        income_stmt: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ratios_dict, error_message)
    """
    try:
        period_idx = _to_int(period_idx, 0)
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], period_idx)
        gross_profit = _get_value(income_stmt, INCOME_FIELDS['gross_profit'], period_idx)
        operating_income = _get_value(income_stmt, INCOME_FIELDS['operating_income'], period_idx)
        net_income = _get_value(income_stmt, INCOME_FIELDS['net_income'], period_idx)
        
        total_equity = _get_value(balance_sheet, BALANCE_FIELDS['total_equity'], period_idx)
        total_assets = _get_value(balance_sheet, BALANCE_FIELDS['total_assets'], period_idx)
        total_debt = _get_value(balance_sheet, BALANCE_FIELDS['total_debt'], period_idx)
        
        ratios = {
            'gross_margin': _safe_divide(gross_profit, revenue),
            'operating_margin': _safe_divide(operating_income, revenue),
            'net_margin': _safe_divide(net_income, revenue),
            'roe': _safe_divide(net_income, total_equity),
            'roa': _safe_divide(net_income, total_assets),
        }
        
        # ROIC = NOPAT / Invested Capital (using 25% tax estimate)
        if operating_income is not None:
            nopat = operating_income * 0.75
            invested_capital = (total_equity or 0) + (total_debt or 0)
            ratios['roic'] = _safe_divide(nopat, invested_capital) if invested_capital > 0 else None
        else:
            ratios['roic'] = None
        
        return ratios, None
        
    except Exception as e:
        logger.error(f"Error calculating profitability ratios: {e}")
        return {}, str(e)


# =============================================================================
# LEVERAGE RATIOS
# =============================================================================

def calculate_leverage_ratios(
    balance_sheet: pd.DataFrame,
    income_stmt: pd.DataFrame = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate leverage/solvency ratios.
    
    Args:
        balance_sheet: Balance sheet DataFrame
        income_stmt: Income statement DataFrame (optional, for interest coverage)
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ratios_dict, error_message)
    """
    try:
        period_idx = _to_int(period_idx, 0)
        balance_sheet = _ensure_dataframe(balance_sheet)
        income_stmt = _ensure_dataframe(income_stmt) if income_stmt is not None else pd.DataFrame()
        
        total_debt = _get_value(balance_sheet, BALANCE_FIELDS['total_debt'], period_idx)
        long_term_debt = _get_value(balance_sheet, BALANCE_FIELDS['long_term_debt'], period_idx)
        short_term_debt = _get_value(balance_sheet, BALANCE_FIELDS['short_term_debt'], period_idx)
        
        # Sum components if total not available
        if total_debt is None and (long_term_debt or short_term_debt):
            total_debt = (long_term_debt or 0) + (short_term_debt or 0)
        
        total_equity = _get_value(balance_sheet, BALANCE_FIELDS['total_equity'], period_idx)
        total_assets = _get_value(balance_sheet, BALANCE_FIELDS['total_assets'], period_idx)
        
        ratios = {
            'debt_to_equity': _safe_divide(total_debt, total_equity),
            'debt_to_assets': _safe_divide(total_debt, total_assets),
            'equity_multiplier': _safe_divide(total_assets, total_equity),
        }
        
        # Interest coverage requires income statement
        if income_stmt is not None and not income_stmt.empty:
            operating_income = _get_value(income_stmt, INCOME_FIELDS['operating_income'], period_idx)
            interest_expense = _get_value(income_stmt, INCOME_FIELDS['interest_expense'], period_idx)
            depreciation = _get_value(income_stmt, INCOME_FIELDS['depreciation'], period_idx)
            
            if interest_expense and interest_expense > 0:
                ratios['interest_coverage'] = _safe_divide(operating_income, interest_expense)
            else:
                ratios['interest_coverage'] = None
            
            # Debt to EBITDA
            if operating_income is not None:
                ebitda = operating_income + (depreciation or 0)
                ratios['debt_to_ebitda'] = _safe_divide(total_debt, ebitda)
            else:
                ratios['debt_to_ebitda'] = None
        
        return ratios, None
        
    except Exception as e:
        logger.error(f"Error calculating leverage ratios: {e}")
        return {}, str(e)


# =============================================================================
# LIQUIDITY RATIOS
# =============================================================================

def calculate_liquidity_ratios(
    balance_sheet: pd.DataFrame,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate liquidity ratios.
    
    Args:
        balance_sheet: Balance sheet DataFrame
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ratios_dict, error_message)
    """
    try:
        period_idx = _to_int(period_idx, 0)
        balance_sheet = _ensure_dataframe(balance_sheet)
        
        current_assets = _get_value(balance_sheet, BALANCE_FIELDS['current_assets'], period_idx)
        current_liabilities = _get_value(balance_sheet, BALANCE_FIELDS['current_liabilities'], period_idx)
        inventory = _get_value(balance_sheet, BALANCE_FIELDS['inventory'], period_idx)
        cash = _get_value(balance_sheet, BALANCE_FIELDS['cash'], period_idx)
        
        ratios = {
            'current_ratio': _safe_divide(current_assets, current_liabilities),
            'cash_ratio': _safe_divide(cash, current_liabilities),
        }
        
        # Quick ratio = (Current Assets - Inventory) / Current Liabilities
        if current_assets is not None:
            quick_assets = current_assets - (inventory or 0)
            ratios['quick_ratio'] = _safe_divide(quick_assets, current_liabilities)
        else:
            ratios['quick_ratio'] = None
        
        # Working capital
        if current_assets is not None and current_liabilities is not None:
            ratios['working_capital'] = current_assets - current_liabilities
        else:
            ratios['working_capital'] = None
        
        return ratios, None
        
    except Exception as e:
        logger.error(f"Error calculating liquidity ratios: {e}")
        return {}, str(e)


# =============================================================================
# EFFICIENCY RATIOS
# =============================================================================

def calculate_efficiency_ratios(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate efficiency/activity ratios.
    
    Args:
        income_stmt: Income statement DataFrame
        balance_sheet: Balance sheet DataFrame
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ratios_dict, error_message)
    """
    try:
        period_idx = _to_int(period_idx, 0)
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        
        revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], period_idx)
        cogs = _get_value(income_stmt, INCOME_FIELDS['cost_of_revenue'], period_idx)
        
        total_assets = _get_value(balance_sheet, BALANCE_FIELDS['total_assets'], period_idx)
        inventory = _get_value(balance_sheet, BALANCE_FIELDS['inventory'], period_idx)
        receivables = _get_value(balance_sheet, BALANCE_FIELDS['receivables'], period_idx)
        payables = _get_value(balance_sheet, BALANCE_FIELDS['payables'], period_idx)
        
        ratios = {
            'asset_turnover': _safe_divide(revenue, total_assets),
            'inventory_turnover': _safe_divide(cogs, inventory),
            'receivables_turnover': _safe_divide(revenue, receivables),
            'payables_turnover': _safe_divide(cogs, payables),
        }
        
        # Days calculations (annual figures)
        ratios['days_inventory'] = _safe_divide(365, ratios['inventory_turnover'])
        ratios['days_receivables'] = _safe_divide(365, ratios['receivables_turnover'])
        ratios['days_payables'] = _safe_divide(365, ratios['payables_turnover'])
        
        # Cash Conversion Cycle = DIO + DSO - DPO
        dio = ratios.get('days_inventory')
        dso = ratios.get('days_receivables')
        dpo = ratios.get('days_payables')
        
        if all(v is not None for v in [dio, dso, dpo]):
            ratios['cash_conversion_cycle'] = dio + dso - dpo
        else:
            ratios['cash_conversion_cycle'] = None
        
        return ratios, None
        
    except Exception as e:
        logger.error(f"Error calculating efficiency ratios: {e}")
        return {}, str(e)


# =============================================================================
# CASH FLOW RATIOS
# =============================================================================

def calculate_cashflow_ratios(
    cash_flow: pd.DataFrame,
    income_stmt: pd.DataFrame = None,
    balance_sheet: pd.DataFrame = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Optional[float]], Optional[str]]:
    """
    Calculate cash flow quality ratios.
    
    Args:
        cash_flow: Cash flow statement DataFrame
        income_stmt: Income statement DataFrame (optional)
        balance_sheet: Balance sheet DataFrame (optional)
        period_idx: Which period (0=most recent)
    
    Returns:
        Tuple of (ratios_dict, error_message)
    """
    try:
        period_idx = _to_int(period_idx, 0)
        cash_flow = _ensure_dataframe(cash_flow)
        income_stmt = _ensure_dataframe(income_stmt) if income_stmt is not None else pd.DataFrame()
        balance_sheet = _ensure_dataframe(balance_sheet) if balance_sheet is not None else pd.DataFrame()
        
        ocf = _get_value(cash_flow, CASHFLOW_FIELDS['operating_cash_flow'], period_idx)
        capex = _get_value(cash_flow, CASHFLOW_FIELDS['capital_expenditure'], period_idx)
        fcf = _get_value(cash_flow, CASHFLOW_FIELDS['free_cash_flow'], period_idx)
        
        # Calculate FCF if not directly available
        if fcf is None and ocf is not None and capex is not None:
            fcf = ocf + capex  # capex is typically negative
        
        ratios = {
            'operating_cash_flow': ocf,
            'free_cash_flow': fcf,
            'capex': capex,
        }
        
        # Cash flow to net income ratio (earnings quality)
        if income_stmt is not None and not income_stmt.empty:
            net_income = _get_value(income_stmt, INCOME_FIELDS['net_income'], period_idx)
            ratios['ocf_to_net_income'] = _safe_divide(ocf, net_income)
        
        # FCF to revenue
        if income_stmt is not None and not income_stmt.empty:
            revenue = _get_value(income_stmt, INCOME_FIELDS['revenue'], period_idx)
            ratios['fcf_margin'] = _safe_divide(fcf, revenue)
        
        # FCF to debt (debt coverage)
        if balance_sheet is not None and not balance_sheet.empty:
            total_debt = _get_value(balance_sheet, BALANCE_FIELDS['total_debt'], period_idx)
            ratios['fcf_to_debt'] = _safe_divide(fcf, total_debt)
        
        return ratios, None
        
    except Exception as e:
        logger.error(f"Error calculating cash flow ratios: {e}")
        return {}, str(e)


# =============================================================================
# UMBRELLA FUNCTION - Main Entry Point
# =============================================================================

def calculate_financial_ratios(
    income_stmt: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cash_flow: pd.DataFrame = None,
    period_idx: int = 0,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Calculate all fundamental ratios from financial statements.
    
    This is the main entry point called by task configs via:
        service: analytics_service
        method: calculate_financial_ratios
    
    Args:
        income_stmt: Income statement DataFrame (yfinance format)
        balance_sheet: Balance sheet DataFrame (yfinance format)
        cash_flow: Cash flow statement DataFrame (optional)
        period_idx: Which period to analyze (0=most recent)
    
    Returns:
        Tuple of (result_dict, error_string or None)
    """
    try:
        # Coerce period_idx to int (may come as string from resolver)
        period_idx = _to_int(period_idx, 0)
        
        # Ensure valid DataFrames
        income_stmt = _ensure_dataframe(income_stmt)
        balance_sheet = _ensure_dataframe(balance_sheet)
        cash_flow = _ensure_dataframe(cash_flow) if cash_flow is not None else pd.DataFrame()
        
        result = {
            'success': True,
            'period_idx': period_idx,
            'calculated_at': datetime.now(timezone.utc).isoformat(),
            'errors': {},
        }
        
        # Get period date if available
        if not income_stmt.empty and len(income_stmt.columns) > period_idx:
            result['period_date'] = str(income_stmt.columns[period_idx])
        
        # Calculate each category
        profitability, err = calculate_profitability_ratios(income_stmt, balance_sheet, period_idx)
        if err:
            result['errors']['profitability'] = err
        result['profitability'] = profitability
        
        leverage, err = calculate_leverage_ratios(balance_sheet, income_stmt, period_idx)
        if err:
            result['errors']['leverage'] = err
        result['leverage'] = leverage
        
        liquidity, err = calculate_liquidity_ratios(balance_sheet, period_idx)
        if err:
            result['errors']['liquidity'] = err
        result['liquidity'] = liquidity
        
        efficiency, err = calculate_efficiency_ratios(income_stmt, balance_sheet, period_idx)
        if err:
            result['errors']['efficiency'] = err
        result['efficiency'] = efficiency
        
        if cash_flow is not None and not cash_flow.empty:
            cashflow_ratios, err = calculate_cashflow_ratios(
                cash_flow, income_stmt, balance_sheet, period_idx
            )
            if err:
                result['errors']['cash_flow'] = err
            result['cash_flow'] = cashflow_ratios
        
        # Mark as failed if all categories errored
        if len(result['errors']) >= 4:
            result['success'] = False
        
        return result, None
        
    except Exception as e:
        logger.error(f"Error in calculate_financial_ratios: {e}")
        return {'success': False, 'error': str(e)}, str(e)