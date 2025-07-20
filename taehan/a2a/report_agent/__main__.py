import logging
import os
import sys

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

from agent import FinancialReportAgent
from agent_executor import FinancialReportAgentExecutor


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10002)
def main(host, port):
    """Starts the Financial Report Agent server."""
    try:
        if os.getenv('model_source',"google") == "google":
           if not os.getenv('GOOGLE_API_KEY'):
               raise MissingAPIKeyError(
                   'GOOGLE_API_KEY environment variable not set.'
               )
        else:
            
            if not os.getenv('TOOL_LLM_URL'):
                raise MissingAPIKeyError(
                    'TOOL_LLM_URL environment variable not set.'
                )
            if not os.getenv('TOOL_LLM_NAME'):
                raise MissingAPIKeyError(
                    'TOOL_LLM_NAME environment not variable not set.'
                )
    
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
        skill = AgentSkill(
            id='financial_report_info',
            name='Financial Report Tool',
            description='Provides comprehensive collection and organization of key financial information',
            tags=['finance report', 'analysis', '금융 시장', '주식', '금융 보고서', '전망', '시장 동향'],
            examples=[
                '오늘의 금융 시장 동향과 투자 전략을 분석하여 보고서를 작성해주세요',
                'GS 주식과 비트코인 전망에 대해서 알려주세요.',
                '오늘의 금융 보고서를 작성해주세요'
            ],
        )
        agent_card = AgentCard(
            name='Financial Report Agent',
            description='Helps with financial market trend analysis and creates investment strategy reports',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=FinancialReportAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=FinancialReportAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        # --8<-- [start:DefaultRequestHandler]
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=FinancialReportAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        uvicorn.run(server.build(), host=host, port=port)
        # --8<-- [end:DefaultRequestHandler]

    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()