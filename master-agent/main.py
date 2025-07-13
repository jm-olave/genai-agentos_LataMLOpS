import asyncio
from typing import Any, Optional

from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from langchain_core.messages import SystemMessage
from loguru import logger

from agents.react_master_agent import ReActMasterAgent
from config.settings import Settings
from llms import LLMFactory
from prompts import FILE_RELATED_SYSTEM_PROMPT, MEXICAN_OIL_FORECASTING_PROMPT
from utils.agents import get_agents
from utils.chat_history import get_chat_history
from utils.common import attach_files_to_message
import re

app_settings = Settings()

session = GenAISession(
    api_key=app_settings.MASTER_AGENT_API_KEY,
    ws_url=app_settings.ROUTER_WS_URL
)


@session.bind(name="MasterAgent", description="Master agent that orchestrates other agents")
async def receive_message(
        agent_context: GenAIContext,
        session_id: str,
        user_id: str,
        configs: dict[str, Any],
        files: Optional[list[dict[str, Any]]],
        timestamp: str
):
    try:
        graph_config = {"configurable": {"session": session}, "recursion_limit": 100}  # recursion_limit can be adjusted

        base_system_prompt = configs.get("system_prompt")
        user_system_prompt = configs.get("user_prompt")

        # Check if this is a Mexican oil forecasting query
        is_oil_forecasting_query = await _is_oil_forecasting_query(chat_history)
        
        if is_oil_forecasting_query:
            system_prompt = MEXICAN_OIL_FORECASTING_PROMPT
        else:
            system_prompt = user_system_prompt or base_system_prompt
            
        system_prompt = f"{system_prompt}\n\n{FILE_RELATED_SYSTEM_PROMPT}"

        chat_history = await get_chat_history(
            f"{app_settings.BACKEND_API_URL}/chat",
            session_id=session_id,
            user_id=user_id,
            api_key=app_settings.MASTER_BE_API_KEY,
            max_last_messages=configs.get("max_last_messages", 5)
        )

        chat_history[-1] = attach_files_to_message(message=chat_history[-1], files=files) if files else chat_history[-1]
        init_messages = [
            SystemMessage(content=system_prompt),
            *chat_history
        ]

        agents = await get_agents(
            url=f"{app_settings.BACKEND_API_URL}/agents/active",
            agent_type="all",
            api_key=app_settings.MASTER_BE_API_KEY,
            user_id=user_id
        )

        llm = LLMFactory.create(configs=configs)
        master_agent = ReActMasterAgent(model=llm, agents=agents)

        logger.info("Running Master Agent")

        final_state = await master_agent.graph.ainvoke(
            input={"messages": init_messages},
            config=graph_config
        )

        response = final_state["messages"][-1].content

        logger.success("Master Agent run successfully")

        return {"agents_trace": final_state["trace"], "response": response, "is_success": True}

    except Exception as e:
        error_message = f"Unexpected error while running Master Agent: {e}"
        logger.exception(error_message)

        trace = {
            "name": "MasterAgent",
            "output": error_message,
            "is_success": False
        }
        return {"agents_trace": [trace], "response": error_message, "is_success": False}


async def _is_oil_forecasting_query(chat_history: list) -> bool:
    """
    Detect if the user query is related to Mexican oil production forecasting.
    """
    if not chat_history:
        return False
    
    # Get the latest user message
    latest_message = chat_history[-1].content if hasattr(chat_history[-1], 'content') else str(chat_history[-1])
    
    # Keywords that indicate oil forecasting queries
    oil_keywords = [
        'oil', 'petroleum', 'crude', 'barrel', 'production', 'forecast', 'predict',
        'mexican', 'mexico', 'ku-maloob-zaap', 'cantarell', 'field', 'reservoir',
        'federal tax', 'revenue', 'economic impact', 'trade balance', 'credit rating'
    ]
    
    # Check if any oil-related keywords are present
    message_lower = latest_message.lower()
    has_oil_keywords = any(keyword in message_lower for keyword in oil_keywords)
    
    # Check for specific patterns
    oil_patterns = [
        r'forecast.*oil.*production',
        r'oil.*production.*forecast',
        r'mexican.*oil',
        r'economic.*impact.*oil',
        r'federal.*tax.*revenue',
        r'ku-maloob-zaap',
        r'cantarell'
    ]
    
    has_oil_patterns = any(re.search(pattern, message_lower) for pattern in oil_patterns)
    
    return has_oil_keywords or has_oil_patterns


async def main():
    logger.info("Master Agent started")
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main())
