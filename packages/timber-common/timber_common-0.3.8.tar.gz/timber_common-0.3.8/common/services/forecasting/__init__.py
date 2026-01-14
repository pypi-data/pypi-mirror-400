"""
Forecasting Service

A lightweight, signal-based ensemble forecasting system.

Architecture:
    Signal -> Features -> Model -> Ensemble -> Forecast

Components:
    - Signal Generators: Technical, Sentiment, Macro, Momentum
    - Models: Ridge, ExpSmooth, Momentum, MeanReversion
    - Ensemble: Dynamic-weighted combination
    - Context: Data aggregation from multiple sources

Usage:
    from common.services.forecasting import forecast_service
    
    result, error = forecast_service.forecast(
        symbol='AAPL',
        price_data=df,
        news=news_list,
        sector_data=sector_dict
    )
"""

# Core types
from .core import (
    Signal,
    SignalDirection,
    TimeHorizon,
    ForecastResult,
    SignalGenerator,
    ForecastModel,
)

# Signal generators
from .signals import (
    TechnicalSignalGenerator,
    SentimentSignalGenerator,
    MacroSignalGenerator,
    MomentumReversionGenerator,
)

# Forecast models
from .models import (
    RidgeRegressor,
    ExponentialSmoother,
    MomentumModel,
    MeanReversionModel,
)

# Ensemble
from .ensemble import EnsembleForecaster

# Context building
from .context import (
    ContextBuilder,
    ContextConfig,
    SectorProfile,
    IndustryProfile,
    PoliticalContext,
    GeographicContext,
    EconomicContext,
)

# Main service
from .service import (
    ForecastService,
    IntegratedForecaster,
    create_forecast_service,
    create_integrated_forecaster,
    forecast_service,
)


__all__ = [
    # Core
    'Signal',
    'SignalDirection', 
    'TimeHorizon',
    'ForecastResult',
    'SignalGenerator',
    'ForecastModel',
    
    # Signals
    'TechnicalSignalGenerator',
    'SentimentSignalGenerator',
    'MacroSignalGenerator',
    'MomentumReversionGenerator',
    
    # Models
    'RidgeRegressor',
    'ExponentialSmoother',
    'MomentumModel',
    'MeanReversionModel',
    
    # Ensemble
    'EnsembleForecaster',
    
    # Context
    'ContextBuilder',
    'ContextConfig',
    'SectorProfile',
    'IndustryProfile',
    'PoliticalContext',
    'GeographicContext',
    'EconomicContext',
    
    # Service
    'ForecastService',
    'IntegratedForecaster',
    'create_forecast_service',
    'create_integrated_forecaster',
    'forecast_service',
]
