import asyncio
import numpy as np
from typing import Annotated, Dict, Any, List
from datetime import datetime, timedelta
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0NmZjNzM4Yy1iMjhhLTRiZTMtYTQ5NS01MzZjYjlkNjU3NjMiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjE4OGM2NDIyLTIwY2MtNDRlNS1hMzc2LTIxMTIwOWJkNDgzNyJ9.8wsNdHhXM8y-C_Mpr_36cCsiSPke5_e-3gyyGo9Hr8U" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT, ws_url="ws://localhost:8081/ws")

@session.bind(
    name="economic_impact_agent",
    description="Economic impact agent that calculates fiscal income, trade balance, and sovereign credit rating impacts from oil production forecasts"
)
async def economic_impact_agent(
    agent_context: GenAIContext,
    field_name: Annotated[str, "Oil field name"],
    production_forecast: Annotated[Dict[str, Any], "Production forecast from modeling agent"],
    analysis_components: Annotated[List[str], "Components to analyze"] = ["federal_tax_revenue", "trade_balance", "sovereign_credit_rating"],
    scenario_analysis: Annotated[bool, "Whether to perform scenario analysis"] = True,
    historical_economic_data: Annotated[Dict[str, Any], "Historical economic data"] = {}
) -> Dict[str, Any]:
    """
    Economic Impact Agent that calculates the economic and fiscal impacts of oil production forecasts.
    
    This agent:
    1. Calculates federal tax revenue impacts
    2. Analyzes trade balance effects
    3. Assesses sovereign credit rating implications
    4. Performs scenario analysis
    5. Provides economic policy recommendations
    """
    
    agent_context.logger.info(f"Starting economic impact analysis for {field_name}")
    
    try:
        # Step 1: Extract production data
        agent_context.logger.info("Extracting production forecast data")
        production_data = await _extract_production_data(production_forecast)
        
        # Step 2: Calculate Federal Tax Revenue Impact
        federal_tax_impact = None
        if "federal_tax_revenue" in analysis_components:
            agent_context.logger.info("Calculating federal tax revenue impact")
            federal_tax_impact = await _calculate_federal_tax_impact(production_data, historical_economic_data)
        
        # Step 3: Analyze Trade Balance Impact
        trade_balance_impact = None
        if "trade_balance" in analysis_components:
            agent_context.logger.info("Analyzing trade balance impact")
            trade_balance_impact = await _analyze_trade_balance_impact(production_data, historical_economic_data)
        
        # Step 4: Assess Sovereign Credit Rating Impact
        credit_rating_impact = None
        if "sovereign_credit_rating" in analysis_components:
            agent_context.logger.info("Assessing sovereign credit rating impact")
            credit_rating_impact = await _assess_credit_rating_impact(production_data, federal_tax_impact, trade_balance_impact)
        
        # Step 5: Perform Scenario Analysis
        scenario_results = None
        if scenario_analysis:
            agent_context.logger.info("Performing scenario analysis")
            scenario_results = await _perform_scenario_analysis(production_data, analysis_components)
        
        # Step 6: Generate Economic Policy Recommendations
        policy_recommendations = await _generate_policy_recommendations(
            federal_tax_impact, trade_balance_impact, credit_rating_impact, scenario_results
        )
        
        result = {
            "field_name": field_name,
            "analysis_components": analysis_components,
            "federal_tax_revenue": federal_tax_impact,
            "trade_balance": trade_balance_impact,
            "sovereign_credit_rating": credit_rating_impact,
            "scenario_analysis": scenario_results,
            "policy_recommendations": policy_recommendations,
            "economic_indicators": {
                "gdp_impact": await _calculate_gdp_impact(production_data),
                "employment_impact": await _calculate_employment_impact(production_data),
                "inflation_impact": await _calculate_inflation_impact(production_data)
            },
            "risk_factors": await _identify_economic_risks(production_data, federal_tax_impact),
            "timestamp": agent_context.timestamp
        }
        
        agent_context.logger.info(f"Completed economic impact analysis for {field_name}")
        return result
        
    except Exception as e:
        agent_context.logger.error(f"Error in economic impact agent: {str(e)}")
        return {
            "error": str(e),
            "field_name": field_name,
            "analysis_components": analysis_components
        }

async def _extract_production_data(production_forecast: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and structure production data for economic analysis"""
    forecast = production_forecast.get("forecast", {})
    return {
        "monthly_production": forecast.get("monthly_production", {}),
        "annual_production": forecast.get("annual_production", {}),
        "cumulative_production": forecast.get("cumulative_production", 0),
        "confidence_intervals": production_forecast.get("confidence_intervals", {}),
        "forecast_period": production_forecast.get("forecast_period", "2 years")
    }

async def _calculate_federal_tax_impact(production_data: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate federal tax revenue impact from oil production"""
    # Mock calculations based on Mexican oil taxation
    oil_price_per_barrel = 80.0  # USD
    federal_tax_rate = 0.30  # 30% federal tax rate
    royalty_rate = 0.075  # 7.5% royalty rate
    
    annual_production = production_data.get("annual_production", {})
    total_tax_revenue = 0
    tax_by_year = {}
    
    for year, production in annual_production.items():
        if isinstance(production, (int, float)):
            revenue = production * oil_price_per_barrel
            federal_tax = revenue * federal_tax_rate
            royalties = revenue * royalty_rate
            total_tax = federal_tax + royalties
            
            tax_by_year[year] = {
                "production_volume": production,
                "revenue": revenue,
                "federal_tax": federal_tax,
                "royalties": royalties,
                "total_tax_revenue": total_tax
            }
            total_tax_revenue += total_tax
    
    return {
        "total_tax_revenue": total_tax_revenue,
        "tax_by_year": tax_by_year,
        "tax_rate_breakdown": {
            "federal_tax_rate": federal_tax_rate,
            "royalty_rate": royalty_rate,
            "effective_tax_rate": federal_tax_rate + royalty_rate
        },
        "revenue_volatility": np.std(list(tax_by_year.values())) if tax_by_year else 0
    }

async def _analyze_trade_balance_impact(production_data: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze impact on Mexico's trade balance"""
    oil_price_per_barrel = 80.0
    import_substitution_rate = 0.15  # 15% of production reduces imports
    
    annual_production = production_data.get("annual_production", {})
    trade_balance_impact = {}
    total_import_reduction = 0
    
    for year, production in annual_production.items():
        if isinstance(production, (int, float)):
            import_reduction = production * import_substitution_rate * oil_price_per_barrel
            export_contribution = production * oil_price_per_barrel
            
            trade_balance_impact[year] = {
                "production_volume": production,
                "import_reduction": import_reduction,
                "export_contribution": export_contribution,
                "net_trade_balance_impact": export_contribution + import_reduction
            }
            total_import_reduction += import_reduction
    
    return {
        "total_import_reduction": total_import_reduction,
        "trade_balance_by_year": trade_balance_impact,
        "current_account_impact": total_import_reduction * 0.8,  # 80% flows to current account
        "balance_of_payments_improvement": total_import_reduction * 0.6
    }

async def _assess_credit_rating_impact(production_data: Dict[str, Any], tax_impact: Dict[str, Any], trade_impact: Dict[str, Any]) -> Dict[str, Any]:
    """Assess impact on sovereign credit rating"""
    # Mock credit rating analysis
    base_rating = "BBB"  # Current Mexican sovereign rating
    
    # Factors affecting credit rating
    fiscal_strength = tax_impact.get("total_tax_revenue", 0) / 1000000000  # Billions USD
    external_position = trade_impact.get("total_import_reduction", 0) / 1000000000
    economic_diversification = 0.7  # Oil dependency factor
    
    # Calculate rating impact
    rating_factors = {
        "fiscal_strength": min(fiscal_strength * 0.1, 0.2),  # Max 0.2 improvement
        "external_position": min(external_position * 0.05, 0.15),  # Max 0.15 improvement
        "economic_stability": 0.1 if economic_diversification > 0.6 else -0.1
    }
    
    total_rating_impact = sum(rating_factors.values())
    
    # Determine new rating
    rating_scale = ["CCC", "B", "BB", "BBB", "A", "AA", "AAA"]
    current_index = rating_scale.index(base_rating)
    new_index = max(0, min(len(rating_scale) - 1, current_index + int(total_rating_impact * 10)))
    new_rating = rating_scale[new_index]
    
    return {
        "current_rating": base_rating,
        "projected_rating": new_rating,
        "rating_change": "upgrade" if new_rating > base_rating else "downgrade" if new_rating < base_rating else "stable",
        "rating_factors": rating_factors,
        "total_rating_impact": total_rating_impact,
        "confidence_level": 0.75
    }

async def _perform_scenario_analysis(production_data: Dict[str, Any], components: List[str]) -> Dict[str, Any]:
    """Perform scenario analysis with different oil prices and production levels"""
    scenarios = {
        "baseline": {"oil_price": 80, "production_multiplier": 1.0},
        "optimistic": {"oil_price": 100, "production_multiplier": 1.2},
        "pessimistic": {"oil_price": 60, "production_multiplier": 0.8}
    }
    
    scenario_results = {}
    
    for scenario_name, params in scenarios.items():
        scenario_results[scenario_name] = {
            "oil_price": params["oil_price"],
            "production_adjustment": params["production_multiplier"],
            "fiscal_impact": await _calculate_scenario_fiscal_impact(production_data, params),
            "trade_impact": await _calculate_scenario_trade_impact(production_data, params),
            "credit_rating_impact": await _calculate_scenario_credit_impact(production_data, params)
        }
    
    return scenario_results

async def _calculate_scenario_fiscal_impact(production_data: Dict[str, Any], scenario_params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate fiscal impact for a specific scenario"""
    oil_price = scenario_params["oil_price"]
    multiplier = scenario_params["production_multiplier"]
    
    # Simplified calculation
    base_revenue = 1000000000  # 1 billion USD base
    adjusted_revenue = base_revenue * (oil_price / 80) * multiplier
    tax_revenue = adjusted_revenue * 0.375  # 37.5% total tax rate
    
    return {
        "adjusted_revenue": adjusted_revenue,
        "tax_revenue": tax_revenue,
        "revenue_change_percent": ((adjusted_revenue - base_revenue) / base_revenue) * 100
    }

async def _calculate_scenario_trade_impact(production_data: Dict[str, Any], scenario_params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate trade impact for a specific scenario"""
    oil_price = scenario_params["oil_price"]
    multiplier = scenario_params["production_multiplier"]
    
    base_trade_impact = 500000000  # 500 million USD base
    adjusted_impact = base_trade_impact * (oil_price / 80) * multiplier
    
    return {
        "trade_balance_impact": adjusted_impact,
        "impact_change_percent": ((adjusted_impact - base_trade_impact) / base_trade_impact) * 100
    }

async def _calculate_scenario_credit_impact(production_data: Dict[str, Any], scenario_params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate credit rating impact for a specific scenario"""
    oil_price = scenario_params["oil_price"]
    
    # Simplified rating impact calculation
    if oil_price >= 90:
        rating_impact = "upgrade"
    elif oil_price <= 70:
        rating_impact = "downgrade"
    else:
        rating_impact = "stable"
    
    return {
        "rating_impact": rating_impact,
        "confidence_level": 0.8 if oil_price >= 80 else 0.6
    }

async def _generate_policy_recommendations(tax_impact: Dict[str, Any], trade_impact: Dict[str, Any], 
                                         credit_impact: Dict[str, Any], scenarios: Dict[str, Any]) -> List[str]:
    """Generate economic policy recommendations"""
    recommendations = []
    
    if tax_impact:
        recommendations.append("Strengthen fiscal buffers through oil revenue stabilization fund")
        recommendations.append("Diversify revenue sources to reduce oil dependency")
    
    if trade_impact:
        recommendations.append("Invest oil revenues in export diversification programs")
        recommendations.append("Develop strategic petroleum reserves for price stability")
    
    if credit_impact and credit_impact.get("rating_change") == "upgrade":
        recommendations.append("Leverage improved credit rating for infrastructure investment")
    
    if scenarios:
        recommendations.append("Implement countercyclical fiscal policies for oil price volatility")
        recommendations.append("Develop contingency plans for low oil price scenarios")
    
    return recommendations

async def _calculate_gdp_impact(production_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate GDP impact from oil production"""
    # Mock GDP calculation
    oil_sector_gdp_contribution = 0.03  # 3% of GDP
    production_multiplier = 1.5  # Economic multiplier effect
    
    return {
        "gdp_contribution_percent": oil_sector_gdp_contribution * 100,
        "economic_multiplier": production_multiplier,
        "total_gdp_impact": oil_sector_gdp_contribution * production_multiplier
    }

async def _calculate_employment_impact(production_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate employment impact from oil production"""
    # Mock employment calculation
    direct_jobs_per_barrel = 0.0001  # Jobs per barrel produced
    indirect_jobs_multiplier = 3.0  # Indirect jobs multiplier
    
    total_production = production_data.get("cumulative_production", 0)
    direct_jobs = total_production * direct_jobs_per_barrel
    indirect_jobs = direct_jobs * indirect_jobs_multiplier
    
    return {
        "direct_jobs": direct_jobs,
        "indirect_jobs": indirect_jobs,
        "total_jobs": direct_jobs + indirect_jobs,
        "employment_multiplier": indirect_jobs_multiplier
    }

async def _calculate_inflation_impact(production_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate inflation impact from oil production"""
    # Mock inflation calculation
    return {
        "inflation_impact": 0.02,  # 2% inflation impact
        "price_stability_contribution": 0.01,  # 1% price stability contribution
        "net_inflation_effect": 0.01  # Net 1% inflation effect
    }

async def _identify_economic_risks(production_data: Dict[str, Any], tax_impact: Dict[str, Any]) -> List[str]:
    """Identify economic risks from oil production forecasts"""
    risks = [
        "Oil price volatility affecting revenue stability",
        "Over-dependence on oil exports",
        "Dutch disease effects on other sectors",
        "Environmental transition risks",
        "Geopolitical risks affecting oil markets"
    ]
    
    if tax_impact and tax_impact.get("revenue_volatility", 0) > 1000000000:
        risks.append("High revenue volatility requiring fiscal buffers")
    
    return risks

async def main():
    print(f"Mexican Oil Economic Impact Agent started with token: {AGENT_JWT}")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
