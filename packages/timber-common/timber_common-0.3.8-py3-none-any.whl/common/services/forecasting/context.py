"""
Forecast Context Builder

Aggregates data from multiple sources to build rich forecasting context.
Integrates with data_fetcher services.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextConfig:
    """Configuration for context building."""
    include_news: bool = True
    news_limit: int = 20
    news_lookback_days: int = 7
    include_sector: bool = True
    include_industry: bool = True
    include_political: bool = True
    include_geographic: bool = True
    include_economic: bool = True
    include_social: bool = False


@dataclass
class SectorProfile:
    """Sector-level information."""
    name: str
    performance_1m: float = 0.0
    performance_3m: float = 0.0
    rotation_score: float = 0.0
    volatility: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'performance_1m': self.performance_1m,
            'performance_3m': self.performance_3m,
            'rotation_score': self.rotation_score,
            'volatility': self.volatility
        }


@dataclass
class IndustryProfile:
    """Industry-level information."""
    name: str
    trend: str = 'stable'
    competitive_score: float = 0.0
    concentration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'trend': self.trend,
            'competitive_score': self.competitive_score,
            'concentration': self.concentration
        }


@dataclass
class PoliticalContext:
    """Political/regulatory context."""
    regulatory_risk: float = 0.0
    policy_impact: float = 0.0
    policy_type: str = 'neutral'
    trade_exposure: float = 0.0
    trade_sentiment: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'regulatory_risk': self.regulatory_risk,
            'policy_impact': self.policy_impact,
            'type': self.policy_type,
            'trade_exposure': self.trade_exposure,
            'trade_sentiment': self.trade_sentiment
        }


@dataclass
class GeographicContext:
    """Geographic exposure context."""
    concentration: Dict[str, float] = field(default_factory=dict)
    primary_region: str = 'US'
    currency_exposure: float = 0.0
    fx_impact: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'concentration': self.concentration,
            'primary_region': self.primary_region,
            'currency_exposure': self.currency_exposure,
            'fx_impact': self.fx_impact
        }
        for region in self.concentration:
            result[f'{region}_outlook'] = 0.0
        return result


@dataclass
class EconomicContext:
    """Economic indicator context."""
    cycle_phase: str = 'expansion'
    rate_direction: str = 'stable'
    inflation_trend: str = 'stable'
    gdp_growth: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cycle_phase': self.cycle_phase,
            'rate_direction': self.rate_direction,
            'inflation_trend': self.inflation_trend,
            'gdp_growth': self.gdp_growth
        }


class ContextBuilder:
    """
    Builds comprehensive context for forecast generation.
    
    Integrates with StockDataService and other data sources.
    """
    
    def __init__(
        self,
        stock_service=None,
        config: Optional[ContextConfig] = None
    ):
        self.config = config or ContextConfig()
        
        if stock_service is None:
            try:
                from common.services.data_fetcher.stock import stock_data_service
                self.stock_service = stock_data_service
            except ImportError:
                self.stock_service = None
                logger.warning("StockDataService not available")
        else:
            self.stock_service = stock_service
        
        self._sector_cache: Dict[str, SectorProfile] = {}
        self._industry_cache: Dict[str, IndustryProfile] = {}
    
    def build(
        self,
        symbol: str,
        company_info: Optional[Dict] = None,
        price_data: Optional[pd.DataFrame] = None,
        market_data: Optional[pd.DataFrame] = None
    ) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Build complete forecast context for a symbol.
        """
        context = {}
        errors = []
        
        try:
            if company_info is None and self.stock_service:
                company_info, err = self.stock_service.fetch_company_info(symbol)
                if err:
                    errors.append(f"Company info: {err}")
            
            if self.config.include_news:
                news_context, err = self._build_news_context(symbol)
                if err:
                    errors.append(f"News: {err}")
                if news_context:
                    context['news'] = news_context
            
            if self.config.include_sector and company_info:
                sector = company_info.get('sector', 'Unknown')
                sector_context = self._build_sector_context(sector, price_data, market_data)
                context['sector'] = sector_context.to_dict()
            
            if self.config.include_industry and company_info:
                industry = company_info.get('industry', 'Unknown')
                industry_context = self._build_industry_context(industry)
                context['industry'] = industry_context.to_dict()
            
            if self.config.include_political and company_info:
                political_context = self._build_political_context(company_info, symbol)
                context['political'] = political_context.to_dict()
            
            if self.config.include_geographic and company_info:
                geo_context = self._build_geographic_context(company_info)
                context['geographic'] = geo_context.to_dict()
            
            if self.config.include_economic:
                econ_context = self._build_economic_context()
                context['economic'] = econ_context.to_dict()
            
            error_msg = '; '.join(errors) if errors else None
            return context, error_msg
            
        except Exception as e:
            logger.error(f"Context building failed: {e}")
            return context, str(e)
    
    def _build_news_context(self, symbol: str) -> Tuple[List[Dict], Optional[str]]:
        if not self.stock_service:
            return [], "No stock service available"
        
        try:
            news, err = self.stock_service.fetch_news(symbol, limit=self.config.news_limit)
            
            if err:
                return [], err
            
            enriched_news = []
            for item in news:
                enriched = item.copy()
                
                if 'sentiment_score' not in enriched:
                    text = f"{item.get('title', '')} {item.get('summary', '')}"
                    enriched['sentiment_score'] = self._estimate_sentiment(text)
                
                enriched_news.append(enriched)
            
            return enriched_news, None
            
        except Exception as e:
            return [], str(e)
    
    def _build_sector_context(
        self,
        sector: str,
        price_data: Optional[pd.DataFrame],
        market_data: Optional[pd.DataFrame]
    ) -> SectorProfile:
        if sector in self._sector_cache:
            return self._sector_cache[sector]
        
        profile = SectorProfile(name=sector)
        
        if price_data is not None and market_data is not None:
            try:
                close = price_data.get('Close') or price_data.get('close')
                mkt_close = market_data.get('Close') or market_data.get('close')
                
                if close is not None and mkt_close is not None:
                    if len(close) >= 20:
                        stock_ret = (close.iloc[-1] / close.iloc[-20]) - 1
                        mkt_ret = (mkt_close.iloc[-1] / mkt_close.iloc[-20]) - 1
                        profile.performance_1m = stock_ret - mkt_ret
                    
                    if len(close) >= 60:
                        stock_ret = (close.iloc[-1] / close.iloc[-60]) - 1
                        mkt_ret = (mkt_close.iloc[-1] / mkt_close.iloc[-60]) - 1
                        profile.performance_3m = stock_ret - mkt_ret
                        
                        returns = close.pct_change().dropna()
                        profile.volatility = returns.std() * np.sqrt(252)
                    
                    if profile.volatility > 0:
                        profile.rotation_score = np.clip(
                            profile.performance_1m / profile.volatility, -1, 1
                        )
            except Exception as e:
                logger.debug(f"Sector calculation error: {e}")
        
        self._sector_cache[sector] = profile
        return profile
    
    def _build_industry_context(self, industry: str) -> IndustryProfile:
        if industry in self._industry_cache:
            return self._industry_cache[industry]
        
        profile = IndustryProfile(name=industry)
        
        growth_industries = [
            'artificial intelligence', 'cloud', 'cybersecurity',
            'electric vehicles', 'renewable energy', 'biotechnology',
            'semiconductors', 'fintech', 'e-commerce'
        ]
        
        declining_industries = [
            'coal', 'traditional retail', 'print media', 'tobacco'
        ]
        
        industry_lower = industry.lower()
        
        if any(gi in industry_lower for gi in growth_industries):
            profile.trend = 'growing'
            profile.competitive_score = 0.3
        elif any(di in industry_lower for di in declining_industries):
            profile.trend = 'declining'
            profile.competitive_score = -0.3
        
        self._industry_cache[industry] = profile
        return profile
    
    def _build_political_context(
        self,
        company_info: Dict,
        symbol: str
    ) -> PoliticalContext:
        context = PoliticalContext()
        
        sector = company_info.get('sector', '').lower()
        industry = company_info.get('industry', '').lower()
        
        high_reg = ['healthcare', 'financial', 'energy', 'utilities']
        medium_reg = ['technology', 'communication', 'consumer']
        
        if any(s in sector for s in high_reg):
            context.regulatory_risk = 0.7
        elif any(s in sector for s in medium_reg):
            context.regulatory_risk = 0.4
        else:
            context.regulatory_risk = 0.2
        
        export_heavy = ['semiconductor', 'automotive', 'agriculture', 'aerospace']
        if any(e in industry for e in export_heavy):
            context.trade_exposure = 0.6
        else:
            context.trade_exposure = 0.2
        
        return context
    
    def _build_geographic_context(self, company_info: Dict) -> GeographicContext:
        context = GeographicContext()
        
        country = company_info.get('country', 'US')
        
        if country in ['United States', 'US', 'USA']:
            context.concentration = {'US': 0.7, 'International': 0.3}
            context.primary_region = 'US'
            context.currency_exposure = 0.2
        else:
            context.concentration = {'US': 0.3, country: 0.5, 'Other': 0.2}
            context.primary_region = country
            context.currency_exposure = 0.5
        
        return context
    
    def _build_economic_context(self) -> EconomicContext:
        return EconomicContext(
            cycle_phase='expansion',
            rate_direction='stable',
            inflation_trend='stable',
            gdp_growth=0.02
        )
    
    def _estimate_sentiment(self, text: str) -> float:
        text = text.lower()
        
        positive = [
            'surge', 'jump', 'rally', 'gain', 'rise', 'beat', 'exceed',
            'strong', 'growth', 'upgrade', 'bullish', 'positive', 'profit',
            'record', 'high', 'outperform', 'buy', 'recommend', 'success'
        ]
        
        negative = [
            'fall', 'drop', 'plunge', 'decline', 'miss', 'weak', 'loss',
            'downgrade', 'bearish', 'negative', 'concern', 'risk', 'sell',
            'crash', 'low', 'underperform', 'warning', 'cut', 'fail'
        ]
        
        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)
        
        total = pos_count + neg_count
        return (pos_count - neg_count) / total if total > 0 else 0.0
