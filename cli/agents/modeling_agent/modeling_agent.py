import asyncio
import pandas as pd
import numpy as np
from typing import Annotated, Dict, Any, List
from datetime import datetime, timedelta
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0M2NmZjVkMi03NmU5LTRkNmItODkwNC0zNTE1OTdjNTI3YTYiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjE4OGM2NDIyLTIwY2MtNDRlNS1hMzc2LTIxMTIwOWJkNDgzNyJ9.0vYyuyv7Mb7jx_pS8HGVxUQicBmztj4DHUh2mfW9iAY" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT, ws_url="ws://localhost:8081/ws")

@session.bind(
    name="modeling_agent",
    description="AI modeling agent that employs machine learning algorithms and econometric models for oil production forecasting"
)
async def modeling_agent(
    agent_context: GenAIContext,
    field_name: Annotated[str, "Oil field name to forecast"],
    historical_data: Annotated[Dict[str, Any], "Historical production data from data collection agent"],
    forecast_period: Annotated[str, "Forecast period (e.g., '2 years', '6 months')"],
    model_types: Annotated[List[str], "Types of models to use"] = ["time_series", "machine_learning"],
    data_quality_score: Annotated[float, "Data quality score from data collection"] = 0.8
) -> Dict[str, Any]:
    """
    AI Modeling Agent that performs predictive modeling for Mexican oil production.
    
    This agent:
    1. Preprocesses historical data
    2. Applies multiple forecasting models
    3. Evaluates model performance
    4. Generates production forecasts with confidence intervals
    5. Identifies key factors affecting production
    """
    
    agent_context.logger.info(f"Starting predictive modeling for {field_name}")
    
    try:
        # Step 1: Data Preprocessing
        agent_context.logger.info("Preprocessing historical data")
        processed_data = await _preprocess_data(historical_data, field_name)
        
        # Step 2: Model Selection and Training
        agent_context.logger.info("Training forecasting models")
        models = await _train_models(processed_data, model_types)
        
        # Step 3: Generate Forecasts
        agent_context.logger.info("Generating production forecasts")
        forecast_period_months = await _parse_forecast_period(forecast_period)
        forecasts = await _generate_forecasts(models, processed_data, forecast_period_months)
        
        # Step 4: Model Evaluation
        agent_context.logger.info("Evaluating model performance")
        model_accuracy = await _evaluate_models(models, processed_data)
        
        # Step 5: Key Factors Analysis
        agent_context.logger.info("Analyzing key factors")
        key_factors = await _analyze_key_factors(processed_data, forecasts)
        
        # Step 6: Risk Assessment
        agent_context.logger.info("Performing risk assessment")
        risk_assessment = await _assess_risks(forecasts, processed_data)
        
        # Step 7: Generate Recommendations
        recommendations = await _generate_recommendations(forecasts, key_factors, risk_assessment)
        
        result = {
            "field_name": field_name,
            "model_accuracy": model_accuracy,
            "forecast": {
                "monthly_production": forecasts.get("monthly", {}),
                "annual_production": forecasts.get("annual", {}),
                "cumulative_production": forecasts.get("cumulative", 0)
            },
            "confidence_intervals": {
                "lower_bound": forecasts.get("lower_bound", {}),
                "upper_bound": forecasts.get("upper_bound", {}),
                "confidence_level": 0.95
            },
            "key_factors": key_factors,
            "model_used": "ensemble_time_series_ml",
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "data_quality_impact": data_quality_score,
            "forecast_period": forecast_period
        }
        
        agent_context.logger.info(f"Completed modeling for {field_name} with accuracy: {model_accuracy:.2f}")
        return result
        
    except Exception as e:
        agent_context.logger.error(f"Error in modeling agent: {str(e)}")
        return {
            "error": str(e),
            "field_name": field_name,
            "model_accuracy": 0.0,
            "forecast": {},
            "confidence_intervals": {},
            "key_factors": [],
            "recommendations": ["Error occurred during modeling"]
        }

async def _preprocess_data(historical_data: Dict[str, Any], field_name: str) -> Dict[str, Any]:
    """Preprocess historical production data"""
    # This would include data cleaning, normalization, feature engineering
    # For now, returning a mock structure
    return {
        "production_series": historical_data.get("production_data", []),
        "features": ["time", "seasonality", "geological_factors", "economic_indicators"],
        "cleaned_data": True,
        "missing_data_handled": True
    }

async def _train_models(data: Dict[str, Any], model_types: List[str]) -> Dict[str, Any]:
    """Train multiple forecasting models"""
    models = {}
    
    if "time_series" in model_types:
        # Mock ARIMA/SARIMA model
        models["time_series"] = {
            "type": "SARIMA",
            "parameters": {"p": 1, "d": 1, "q": 1, "P": 1, "D": 1, "Q": 1, "s": 12},
            "trained": True
        }
    
    if "machine_learning" in model_types:
        # Mock ML model (XGBoost, Random Forest, etc.)
        models["ml"] = {
            "type": "XGBoost",
            "parameters": {"n_estimators": 100, "max_depth": 6},
            "trained": True
        }
    
    return models

async def _parse_forecast_period(period: str) -> int:
    """Parse forecast period string to number of months"""
    period_lower = period.lower()
    if "year" in period_lower:
        years = int(period.split()[0])
        return years * 12
    elif "month" in period_lower:
        return int(period.split()[0])
    else:
        return 24  # Default to 2 years

async def _generate_forecasts(models: Dict[str, Any], data: Dict[str, Any], months: int) -> Dict[str, Any]:
    """Generate production forecasts"""
    # Mock forecast generation
    base_production = 50000  # barrels per day
    monthly_forecast = {}
    annual_forecast = {}
    
    for i in range(1, months + 1):
        # Simulate declining production with some volatility
        decline_rate = 0.02  # 2% monthly decline
        volatility = np.random.normal(0, 0.05)  # 5% volatility
        production = base_production * (1 - decline_rate) ** i * (1 + volatility)
        
        monthly_forecast[f"month_{i}"] = max(0, production)
    
    # Calculate annual totals
    for year in range(1, (months // 12) + 2):
        year_months = monthly_forecast.get(f"month_{year * 12}", 0)
        annual_forecast[f"year_{year}"] = year_months * 365
    
    return {
        "monthly": monthly_forecast,
        "annual": annual_forecast,
        "cumulative": sum(monthly_forecast.values()) * 30,  # Approximate monthly to cumulative
        "lower_bound": {k: v * 0.9 for k, v in monthly_forecast.items()},
        "upper_bound": {k: v * 1.1 for k, v in monthly_forecast.items()}
    }

async def _evaluate_models(models: Dict[str, Any], data: Dict[str, Any]) -> float:
    """Evaluate model performance"""
    # Mock model evaluation
    return 0.85  # 85% accuracy

async def _analyze_key_factors(data: Dict[str, Any], forecasts: Dict[str, Any]) -> List[str]:
    """Analyze key factors affecting production"""
    return [
        "Reservoir pressure decline",
        "Water cut increase",
        "Equipment maintenance schedules",
        "Economic investment levels",
        "Geological complexity",
        "Environmental regulations"
    ]

async def _assess_risks(forecasts: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess risks in the forecast"""
    return {
        "technical_risks": ["Reservoir performance uncertainty", "Equipment failure"],
        "economic_risks": ["Oil price volatility", "Investment constraints"],
        "regulatory_risks": ["Environmental compliance", "Policy changes"],
        "risk_score": 0.3,  # Low to medium risk
        "mitigation_strategies": [
            "Enhanced monitoring systems",
            "Diversified investment portfolio",
            "Regulatory compliance programs"
        ]
    }

async def _generate_recommendations(forecasts: Dict[str, Any], key_factors: List[str], risks: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on forecast and analysis"""
    return [
        "Implement enhanced oil recovery techniques",
        "Increase investment in maintenance and monitoring",
        "Diversify production portfolio",
        "Develop contingency plans for price volatility",
        "Strengthen regulatory compliance programs"
    ]

async def main():
    print(f"Mexican Oil Modeling Agent started with token: {AGENT_JWT}")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
