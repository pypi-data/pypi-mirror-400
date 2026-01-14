"""
Forecast Service

Main entry point for price forecasting.
"""

import pandas as pd
from typing import Tuple, Optional, List, Dict, Any
import logging

from .core import SignalGenerator, ForecastResult, Signal
from .ensemble import EnsembleForecaster
from .context import ContextBuilder, ContextConfig

logger = logging.getLogger(__name__)


class ForecastService:
    """
    Main entry point for price forecasting.
    
    Orchestrates data collection, signal generation, and forecast production.
    """
    
    def __init__(
        self,
        custom_generators: Optional[List[SignalGenerator]] = None,
        category_weights: Optional[Dict[str, float]] = None
    ):
        self.forecaster = EnsembleForecaster()
        
        if custom_generators:
            self.forecaster.signal_generators.extend(custom_generators)
        
        if category_weights:
            self.forecaster.category_weights.update(category_weights)
    
    def forecast(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        news: Optional[List[Dict]] = None,
        sector_data: Optional[Dict] = None,
        industry_data: Optional[Dict] = None,
        political_data: Optional[Dict] = None,
        geographic_data: Optional[Dict] = None,
        economic_data: Optional[Dict] = None,
        social_data: Optional[Dict] = None,
        horizons: Optional[List[int]] = None
    ) -> Tuple[Optional[ForecastResult], Optional[str]]:
        """
        Generate price forecast.
        
        Args:
            symbol: Stock ticker
            price_data: Historical OHLCV DataFrame
            news: List of news articles
            sector_data: Sector-level data
            industry_data: Industry-level data
            political_data: Political/regulatory data
            geographic_data: Geographic exposure data
            economic_data: Economic indicator data
            social_data: Social media sentiment
            horizons: Forecast horizons in days
            
        Returns:
            Tuple of (ForecastResult, error_message)
        """
        try:
            context = {}
            
            if news:
                context['news'] = news
            if sector_data:
                context['sector'] = sector_data
            if industry_data:
                context['industry'] = industry_data
            if political_data:
                context['political'] = political_data
            if geographic_data:
                context['geographic'] = geographic_data
            if economic_data:
                context['economic'] = economic_data
            if social_data:
                context['social'] = social_data
            
            result = self.forecaster.generate_forecast(
                symbol=symbol,
                price_data=price_data,
                context=context,
                horizons=horizons
            )
            
            return result, None
            
        except Exception as e:
            logger.error(f"Forecast generation failed: {e}")
            return None, f"Forecast failed: {str(e)}"
    
    def quick_forecast(
        self,
        symbol: str,
        price_data: pd.DataFrame
    ) -> Tuple[Optional[ForecastResult], Optional[str]]:
        """
        Generate a quick forecast using only price data.
        """
        return self.forecast(symbol, price_data)
    
    def add_signal_generator(self, generator: SignalGenerator) -> None:
        """Add a custom signal generator."""
        self.forecaster.signal_generators.append(generator)
    
    def set_category_weight(self, category: str, weight: float) -> None:
        """Set weight for a signal category."""
        self.forecaster.category_weights[category] = weight
    
    def get_signal_breakdown(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, List[Signal]], Optional[str]]:
        """
        Get detailed signal breakdown without full forecast.
        """
        try:
            if context is None:
                context = {}
            
            signals_by_category: Dict[str, List[Signal]] = {}
            
            for generator in self.forecaster.signal_generators:
                signals = generator.generate(symbol, price_data, context)
                
                for signal in signals:
                    if signal.category not in signals_by_category:
                        signals_by_category[signal.category] = []
                    signals_by_category[signal.category].append(signal)
            
            return signals_by_category, None
            
        except Exception as e:
            return {}, f"Signal generation failed: {str(e)}"


class IntegratedForecaster:
    """
    High-level forecaster combining context building with forecast generation.
    
    Primary interface for end-to-end forecasting with automatic data fetching.
    """
    
    def __init__(
        self,
        stock_service=None,
        context_config: Optional[ContextConfig] = None
    ):
        self.context_builder = ContextBuilder(
            stock_service=stock_service,
            config=context_config
        )
        self.forecast_service = ForecastService()
    
    def forecast(
        self,
        symbol: str,
        period: str = '1y',
        horizons: Optional[List[int]] = None,
        include_context: bool = True
    ) -> Tuple[Optional[ForecastResult], Optional[str]]:
        """
        Generate a complete forecast for a symbol.
        
        Args:
            symbol: Stock ticker
            period: Historical data period
            horizons: Forecast horizons in days
            include_context: Whether to build full context
        """
        stock_service = self.context_builder.stock_service
        
        if stock_service is None:
            return None, "No stock data service available"
        
        price_data, err = stock_service.fetch_historical_data(symbol, period=period)
        if err:
            return None, f"Failed to fetch price data: {err}"
        
        if price_data.empty:
            return None, "No price data available"
        
        context_kwargs = {}
        if include_context:
            company_info, _ = stock_service.fetch_company_info(symbol)
            context, ctx_err = self.context_builder.build(
                symbol,
                company_info=company_info,
                price_data=price_data
            )
            
            if ctx_err:
                logger.warning(f"Context building had errors: {ctx_err}")
            
            context_kwargs = {
                'news': context.get('news'),
                'sector_data': context.get('sector'),
                'industry_data': context.get('industry'),
                'political_data': context.get('political'),
                'geographic_data': context.get('geographic'),
                'economic_data': context.get('economic')
            }
        
        return self.forecast_service.forecast(
            symbol=symbol,
            price_data=price_data,
            horizons=horizons,
            **context_kwargs
        )
    
    def quick_forecast(
        self,
        symbol: str,
        price_data: pd.DataFrame
    ) -> Tuple[Optional[ForecastResult], Optional[str]]:
        """Generate a quick forecast using only price data."""
        return self.forecast_service.quick_forecast(symbol, price_data)


def create_forecast_service(
    include_technical: bool = True,
    include_sentiment: bool = True,
    include_macro: bool = True,
    include_momentum: bool = True,
    custom_weights: Optional[Dict[str, float]] = None
) -> ForecastService:
    """
    Factory function to create a configured ForecastService.
    """
    from .signals import (
        TechnicalSignalGenerator,
        SentimentSignalGenerator,
        MacroSignalGenerator,
        MomentumReversionGenerator
    )
    
    generators = []
    weights = {}
    
    if include_technical:
        generators.append(TechnicalSignalGenerator())
        weights['technical'] = 0.35
    
    if include_sentiment:
        generators.append(SentimentSignalGenerator())
        weights['sentiment'] = 0.20
    
    if include_macro:
        generators.append(MacroSignalGenerator())
        weights['macro'] = 0.20
    
    if include_momentum:
        generators.append(MomentumReversionGenerator())
        weights['momentum'] = 0.25
    
    if custom_weights:
        weights.update(custom_weights)
    
    # Normalize
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}
    
    service = ForecastService()
    service.forecaster.signal_generators = generators
    service.forecaster.category_weights = weights
    
    return service


def create_integrated_forecaster(
    stock_service=None,
    include_news: bool = True,
    include_macro: bool = True
) -> IntegratedForecaster:
    """Factory function to create a configured IntegratedForecaster."""
    config = ContextConfig(
        include_news=include_news,
        include_sector=include_macro,
        include_industry=include_macro,
        include_political=include_macro,
        include_geographic=include_macro,
        include_economic=include_macro
    )
    
    return IntegratedForecaster(
        stock_service=stock_service,
        context_config=config
    )


# Singleton instance
forecast_service = ForecastService()
