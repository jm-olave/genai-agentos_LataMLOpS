# import asyncio
# from typing import Annotated
# from genai_session.session import GenAISession
# from genai_session.utils.context import GenAIContext
# from datetime import datetime

# AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MzNmNGVkMy0xOWIxLTQ4NDAtODk3OS0zYjMzNzY2NmRiOTgiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjQyOTIxMzlkLWQ1MDUtNDQwOC05ZTNlLWI3M2YxNzMwNTI5NiJ9.BbSVAoKIxY3HW5JZh-QlxYQz0nXtXrHow7S2HMwlHZw" # noqa: E501
# session = GenAISession(jwt_token=AGENT_JWT)


# @session.bind(
#     name="current_date",
#     description="Agent that returns current date"
# )
# async def current_date(agent_context):
#     agent_context.logger.info("Inside get_current_date")
#     return datetime.now().strftime("%Y-%m-%d")

# async def main():
#     print(f"Agent with token '{AGENT_JWT}' started")
#     await session.process_events()

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from datetime import datetime
import json

# Importaciones opcionales
try:
    import pandas as pd
    from prophet import Prophet
    DEPENDENCIES_AVAILABLE = True
    print("✅ Dependencies loaded successfully")
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"❌ Dependencies missing: {e}")

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MzNmNGVkMy0xOWIxLTQ4NDAtODk3OS0zYjMzNzY2NmRiOTgiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6IjQyOTIxMzlkLWQ1MDUtNDQwOC05ZTNlLWI3M2YxNzMwNTI5NiJ9.BbSVAoKIxY3HW5JZh-QlxYQz0nXtXrHow7S2HMwlHZw"
session = GenAISession(jwt_token=AGENT_JWT)

# Cargar dataset al inicio
df_procesado = pd.read_csv("df_processed.csv")

if DEPENDENCIES_AVAILABLE:
    try:
        print("🔄 Loading dataset...")
        df_procesado = pd.read_csv("df_processed.csv")
        print(f"✅ Dataset loaded successfully: {len(df_procesado):,} records")
        print(f"📅 Date range: {df_procesado['FECHA'].min()} to {df_procesado['FECHA'].max()}")
        print(f"🏭 Available fields: {df_procesado['CAMPO_OFICIAL'].nunique()}")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        print("💡 Make sure 'df_processed.csv' exists in the current directory")

def predecir_con_prophet(df, campo, variable_target, meses_futuros):
    """Predicción usando Prophet para un campo específico"""
    try:
        # Filtrar datos del campo
        datos_campo = df[df['CAMPO_OFICIAL'] == campo].copy()
        
        if len(datos_campo) == 0:
            return None, None, f"No data found for field: {campo}"
        
        # Convertir fecha y ordenar
        datos_campo['FECHA'] = pd.to_datetime(datos_campo['FECHA'])
        datos_campo = datos_campo.sort_values('FECHA')
        
        # Preparar datos para Prophet
        datos_prophet = pd.DataFrame({
            'ds': datos_campo['FECHA'],
            'y': datos_campo[variable_target]
        })
        
        # Eliminar valores nulos
        datos_prophet = datos_prophet.dropna()
        
        if len(datos_prophet) < 10:
            return None, None, f"Insufficient data for prediction: only {len(datos_prophet)} valid records"
        
        # Crear modelo Prophet
        modelo = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
            interval_width=0.95
        )
        
        # Agregar estacionalidad mensual
        modelo.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Entrenar modelo
        modelo.fit(datos_prophet)
        
        # Crear fechas futuras
        future = modelo.make_future_dataframe(periods=meses_futuros, freq='M')
        
        # Hacer predicciones
        forecast = modelo.predict(future)
        
        return modelo, forecast, "Success"
        
    except Exception as e:
        return None, None, f"Error in prediction: {str(e)}"

@session.bind(
    name="oil_assistant",
    description="Oil production assistant. Actions: 'date' (current date), 'status' (dataset info), 'list_fields' (available oil fields), 'field_info' (specific field details), 'predict' (make predictions). For predictions, specify field_name, target_variable, and months_ahead."
)
async def oil_assistant(
    agent_context,
    action: Annotated[str, "Action: 'date', 'status', 'list_fields', 'field_info', 'predict'"],
    field_name: Annotated[str, "Oil field name (for field_info and predict)"] = "",
    target_variable: Annotated[str, "Variable to predict"] = "HIDROCARBUROS_LIQUIDOS_MBD",
    months_ahead: Annotated[int, "Months to predict"] = 12
):
    """Asistente de producción petrolera con dataset pre-cargado"""
    
    try:
        # ACCIÓN: Obtener fecha actual
        if action.lower() == "date":
            agent_context.logger.info("Getting current date")
            return datetime.now().strftime("%Y-%m-%d")
        
        # ACCIÓN: Estado del dataset
        elif action.lower() == "status":
            if df_procesado is None:
                return json.dumps({
                    "status": "error",
                    "message": "Dataset not loaded. Check if df_processed.csv exists and dependencies are installed."
                }, indent=2)
            
            campos_disponibles = df_procesado['CAMPO_OFICIAL'].unique().tolist()
            columnas_disponibles = df_procesado.columns.tolist()
            
            return json.dumps({
                "status": "success",
                "message": "Dataset ready for analysis",
                "total_records": len(df_procesado),
                "date_range": {
                    "start": str(df_procesado['FECHA'].min()),
                    "end": str(df_procesado['FECHA'].max())
                },
                "total_fields": len(campos_disponibles),
                "sample_fields": campos_disponibles[:5],
                "available_columns": columnas_disponibles
            }, ensure_ascii=False, indent=2)
        
        # ACCIÓN: Listar campos
        elif action.lower() == "list_fields":
            if df_procesado is None:
                return json.dumps({
                    "status": "error",
                    "message": "Dataset not loaded"
                }, indent=2)
            
            campos = df_procesado['CAMPO_OFICIAL'].unique().tolist()
            
            return json.dumps({
                "status": "success",
                "total_fields": len(campos),
                "available_fields": sorted(campos)
            }, ensure_ascii=False, indent=2)
        
        # ACCIÓN: Información de campo específico
        elif action.lower() == "field_info":
            if df_procesado is None:
                return json.dumps({
                    "status": "error",
                    "message": "Dataset not loaded"
                }, indent=2)
            
            if not field_name:
                return json.dumps({
                    "status": "error",
                    "message": "field_name is required for this action"
                }, indent=2)
            
            # Búsqueda flexible del campo
            campos_similares = df_procesado[df_procesado['CAMPO_OFICIAL'].str.contains(field_name, case=False, na=False)]['CAMPO_OFICIAL'].unique()
            
            if len(campos_similares) == 0:
                return json.dumps({
                    "status": "error",
                    "message": f"Field '{field_name}' not found",
                    "suggestion": "Use action 'list_fields' to see available fields"
                }, indent=2)
            
            campo_encontrado = campos_similares[0]
            datos_campo = df_procesado[df_procesado['CAMPO_OFICIAL'] == campo_encontrado]
            
            return json.dumps({
                "status": "success",
                "field_name": campo_encontrado,
                "total_records": len(datos_campo),
                "date_range": {
                    "start": str(datos_campo['FECHA'].min()),
                    "end": str(datos_campo['FECHA'].max())
                },
                "available_variables": [col for col in datos_campo.columns if col not in ['FECHA', 'CAMPO_OFICIAL']],
                "similar_fields": campos_similares.tolist() if len(campos_similares) > 1 else None
            }, ensure_ascii=False, indent=2)
        
        # ACCIÓN: Predicción
        elif action.lower() == "predict":
            if not DEPENDENCIES_AVAILABLE:
                return json.dumps({
                    "status": "error",
                    "message": "Prophet library required for predictions. Install with: pip install prophet"
                }, indent=2)
            
            if df_procesado is None:
                return json.dumps({
                    "status": "error",
                    "message": "Dataset not loaded"
                }, indent=2)
            
            if not field_name:
                return json.dumps({
                    "status": "error",
                    "message": "field_name is required for predictions"
                }, indent=2)
            
            # Buscar campo
            campos_similares = df_procesado[df_procesado['CAMPO_OFICIAL'].str.contains(field_name, case=False, na=False)]['CAMPO_OFICIAL'].unique()
            
            if len(campos_similares) == 0:
                return json.dumps({
                    "status": "error",
                    "message": f"Field '{field_name}' not found"
                }, indent=2)
            
            campo_encontrado = campos_similares[0]
            
            # Verificar que la variable objetivo existe
            if target_variable not in df_procesado.columns:
                return json.dumps({
                    "status": "error",
                    "message": f"Target variable '{target_variable}' not found",
                    "available_variables": [col for col in df_procesado.columns if col not in ['FECHA', 'CAMPO_OFICIAL']]
                }, indent=2)
            
            agent_context.logger.info(f"Making prediction for {campo_encontrado}, variable: {target_variable}, months: {months_ahead}")
            
            # Hacer predicción
            modelo, predicciones, status_msg = predecir_con_prophet(df_procesado, campo_encontrado, target_variable, months_ahead)
            
            if modelo is None:
                return json.dumps({
                    "status": "error",
                    "message": status_msg
                }, indent=2)
            
            # Preparar resultados
            tabla = predicciones[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(months_ahead).copy()
            tabla.columns = ['Fecha', 'Predicción', 'Límite_Inferior', 'Límite_Superior']
            tabla['Fecha'] = tabla['Fecha'].dt.strftime('%Y-%m')
            tabla = tabla.round(4).reset_index(drop=True)
            
            predicciones_dict = tabla.to_dict('records')
            
            return json.dumps({
                "status": "success",
                "field_name": campo_encontrado,
                "target_variable": target_variable,
                "months_predicted": months_ahead,
                "prediction_summary": {
                    "avg_prediction": round(tabla['Predicción'].mean(), 2),
                    "trend": "increasing" if tabla['Predicción'].iloc[-1] > tabla['Predicción'].iloc[0] else "decreasing"
                },
                "predictions": predicciones_dict
            }, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({
                "status": "error",
                "message": f"Action '{action}' not recognized. Available actions: 'date', 'status', 'list_fields', 'field_info', 'predict'"
            }, indent=2)
    
    except Exception as e:
        agent_context.logger.error(f"Error in oil_assistant: {str(e)}")
        return json.dumps({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }, ensure_ascii=False, indent=2)

async def main():
    print("🛢️  Oil Production Assistant")
    print("📊 Dataset:", "✅ Loaded" if df_procesado is not None else "❌ Not loaded")
    print("🔧 Dependencies:", "✅ Available" if DEPENDENCIES_AVAILABLE else "❌ Missing")
    print("\n🚀 Agent ready for queries!")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())