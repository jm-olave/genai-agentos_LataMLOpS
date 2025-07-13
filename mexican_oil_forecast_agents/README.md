# 🛢️ Mexican Oil Production Forecasting Multi-Agent System

A comprehensive multi-agent system for predictive modeling of Mexican oil production with economic impact analysis.

## 🏗️ System Architecture

This system consists of four specialized agents working together to provide comprehensive oil production forecasting and economic analysis:

### 1. **Master Agent** (`master-agent/main.py`)
- **Type**: Enhanced GenAI Master Agent
- **Purpose**: Orchestrates the entire forecasting workflow using existing ReAct framework
- **Responsibilities**:
  - Receives user queries (e.g., "Forecast oil production for Ku-Maloob-Zaap field for next 2 years")
  - Automatically detects oil forecasting queries and applies specialized prompts
  - Coordinates data collection, modeling, and economic analysis
  - Aggregates results into comprehensive reports
  - Manages the workflow between all agents using LangGraph

### 2. **Data Collection Agent** (`cloudera_mcp_data_collector.py`)
- **Type**: Cloudera MCP Agent
- **Purpose**: Gathers comprehensive oil production data
- **Responsibilities**:
  - Accesses `PRODUCCION_CAMPOS_Jan-25.csv` via Cloudera MCP
  - Collects historical production statistics (pre-2025)
  - Gathers geological information and field characteristics
  - Retrieves macroeconomic variables and indicators
  - Performs data quality assessment and validation

### 3. **AI Modeling Agent** (`modeling_agent.py`)
- **Type**: GenAI Agent
- **Purpose**: Performs predictive modeling and forecasting
- **Responsibilities**:
  - Preprocesses and cleans historical data
  - Applies multiple forecasting models (time series, ML, econometric)
  - Generates production forecasts with confidence intervals
  - Evaluates model performance and accuracy
  - Identifies key factors affecting production
  - Performs risk assessment

### 4. **Economic Impact Agent** (`economic_impact_agent.py`)
- **Type**: GenAI Agent
- **Purpose**: Calculates economic and fiscal impacts
- **Responsibilities**:
  - Calculates federal tax revenue impacts
  - Analyzes trade balance effects
  - Assesses sovereign credit rating implications
  - Performs scenario analysis (optimistic, baseline, pessimistic)
  - Generates economic policy recommendations

## 🚀 Quick Start

### Prerequisites
1. GenAI infrastructure running (backend, router, master-agent)
2. Cloudera MCP server configured
3. Access to `PRODUCCION_CAMPOS_Jan-25.csv` data
4. Python 3.12+ with required dependencies
5. Modeling and Economic Impact agents already registered via CLI

### Setup Instructions

1. **Register Agents with CLI**:
   ```bash
   cd cli
   python cli.py login -u <username> -p <password>
   
   # Register modeling and economic agents (already done)
   # Register data collector agent
   python cli.py register_agent --name mexican_oil_data_collector_mcp --description "Cloudera MCP data collection agent"
   ```

2. **Update JWT Tokens**:
   - Replace `"your-cloudera-mcp-agent-jwt-here"` in `cloudera_mcp_data_collector.py` with actual JWT token
   - The master agent uses the existing infrastructure and doesn't need a separate JWT

3. **Configure Cloudera MCP**:
   - Ensure Cloudera MCP server is running and accessible
   - Configure MCP tools for data access
   - Update MCP connection parameters in `cloudera_mcp_data_collector.py`

4. **Run Agents**:
   ```bash
   # Start the registered agents
   cd cli/agents/modeling_agent
   python modeling_agent.py &
   
   cd ../economic_impact_agent
   python economic_impact_agent.py &
   
   # Start the data collector (after registering)
   cd ../../mexican_oil_forecast_agents
   python cloudera_mcp_data_collector.py &
   
   # The master agent runs as part of the infrastructure
   # (master-agent/main.py is already integrated)
   ```

## 📊 Data Flow

```
User Query → Master Agent → Data Collection (MCP) → AI Modeling → Economic Impact → Comprehensive Report
```

1. **User submits query** via frontend or API
2. **Master Agent** parses query and extracts parameters
3. **Data Collection Agent** (MCP) gathers required data
4. **AI Modeling Agent** processes data and generates forecasts
5. **Economic Impact Agent** calculates fiscal and economic effects
6. **Master Agent** compiles comprehensive results

## 🔧 Configuration

### Environment Variables
```bash
# Required for all agents
ROUTER_WS_URL=ws://localhost:8080/ws
BACKEND_API_URL=http://localhost:8000

# Cloudera MCP specific
CLOUDERA_MCP_URL=http://localhost:8080
CLOUDERA_MCP_API_KEY=your-mcp-api-key

# Data sources
PRODUCCION_CAMPOS_FILE_PATH=/path/to/PRODUCCION_CAMPOS_Jan-25.csv
```

### Agent Parameters

#### Master Agent
- `user_query`: Natural language query from user
- `field_name`: Oil field name (e.g., "Ku-Maloob-Zaap", "Cantarell")
- `forecast_period`: Time period for forecast (e.g., "2 years", "6 months")
- `include_economic_impact`: Boolean for economic analysis

#### Data Collection Agent (MCP)
- `field_name`: Target oil field
- `data_sources`: List of data sources to access
- `time_period`: Historical data period
- `data_requirements`: Specific data requirements

#### Modeling Agent
- `field_name`: Oil field name
- `historical_data`: Data from collection agent
- `forecast_period`: Forecast time period
- `model_types`: Types of models to use
- `data_quality_score`: Quality assessment from data collection

#### Economic Impact Agent
- `field_name`: Oil field name
- `production_forecast`: Forecast from modeling agent
- `analysis_components`: Economic components to analyze
- `scenario_analysis`: Boolean for scenario analysis

## 📈 Output Format

### Comprehensive Report Structure
```json
{
  "field_name": "Ku-Maloob-Zaap",
  "forecast_period": "2 years",
  "user_query": "Forecast oil production for Ku-Maloob-Zaap field for next 2 years",
  "data_collection": {
    "status": "completed",
    "data_points": 120,
    "data_quality_score": 0.85,
    "sources_accessed": ["PRODUCCION_CAMPOS_Jan-25.csv", "historical_production"]
  },
  "production_forecast": {
    "model_accuracy": 0.85,
    "forecast_values": {
      "monthly_production": {...},
      "annual_production": {...},
      "cumulative_production": 15000000
    },
    "confidence_intervals": {
      "lower_bound": {...},
      "upper_bound": {...},
      "confidence_level": 0.95
    },
    "key_factors": ["Reservoir pressure decline", "Water cut increase"],
    "model_used": "ensemble_time_series_ml"
  },
  "economic_impact": {
    "federal_tax_revenue": {
      "total_tax_revenue": 1500000000,
      "tax_by_year": {...}
    },
    "trade_balance": {
      "total_import_reduction": 800000000,
      "trade_balance_by_year": {...}
    },
    "sovereign_credit_rating": {
      "current_rating": "BBB",
      "projected_rating": "A",
      "rating_change": "upgrade"
    },
    "scenario_analysis": {...},
    "policy_recommendations": [...]
  },
  "recommendations": [...],
  "risk_assessment": {...},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🛠️ Development

### Adding New Models
To add new forecasting models, modify the `_train_models()` function in `modeling_agent.py`:

```python
async def _train_models(data: Dict[str, Any], model_types: List[str]) -> Dict[str, Any]:
    models = {}
    
    if "new_model_type" in model_types:
        models["new_model"] = {
            "type": "YourNewModel",
            "parameters": {"param1": value1, "param2": value2},
            "trained": True
        }
    
    return models
```

### Extending Economic Analysis
To add new economic indicators, modify the `economic_impact_agent.py`:

```python
async def _calculate_new_economic_indicator(production_data: Dict[str, Any]) -> Dict[str, Any]:
    # Your calculation logic here
    return {"indicator_name": value, "impact": impact_value}
```

### Customizing MCP Tools
To add new Cloudera MCP tools, update the `_access_production_data_mcp()` function:

```python
async def _access_production_data_mcp(field_name: str, data_sources: List[str]) -> Dict[str, Any]:
    mcp_tools = {
        "your_new_tool": {
            "tool_name": "your_new_tool",
            "description": "Description of your new tool",
            "parameters": {"param1": "value1"}
        }
    }
    # Implementation here
```

## 🧪 Testing

### Unit Tests
```bash
# Test individual agents
python -m pytest tests/test_master_agent.py
python -m pytest tests/test_modeling_agent.py
python -m pytest tests/test_economic_agent.py
python -m pytest tests/test_data_collector.py
```

### Integration Tests
```bash
# Test complete workflow
python -m pytest tests/test_integration.py
```

### Sample Queries
```python
# Test query for Ku-Maloob-Zaap field
{
    "user_query": "Forecast oil production for the Ku-Maloob-Zaap field for the next two years and project the impact on federal tax revenues.",
    "field_name": "Ku-Maloob-Zaap",
    "forecast_period": "2 years",
    "include_economic_impact": True
}
```

## 📚 Dependencies

### Core Dependencies
- `genai-session`: GenAI protocol library
- `pandas`: Data manipulation
- `numpy`: Numerical computations
- `asyncio`: Asynchronous programming

### Optional Dependencies
- `scikit-learn`: Machine learning models
- `statsmodels`: Time series analysis
- `matplotlib`: Data visualization
- `seaborn`: Statistical visualization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section in the main README
2. Review agent logs for error messages
3. Verify MCP server connectivity
4. Ensure all JWT tokens are valid and current 