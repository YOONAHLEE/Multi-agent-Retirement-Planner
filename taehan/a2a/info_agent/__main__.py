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

from agent import RetirementPensionAgent
from agent_executor import RetirementPensionAgentExecutor


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10000)
def main(host, port):
    """Starts the Info Agent server."""
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
            id='retirement_pension_info',
            name='Retirement Pension Information Tool',
            description='Provides comprehensive information about retirement pension options and strategies',
            tags=['retirement', 'pension', 'DB형', 'DC형', 'IRP', '퇴직연금'],
            examples=[
                '퇴직연금 확정급여형(DB형)과 확정기여형(DC형)의 차이점은?',
                '노후 대비를 위한 회사 제공 자산관리 옵션은 뭐가 있어?',
                '퇴직연금 종류와 특징을 알려줘'
            ],
        )
        agent_card = AgentCard(
            name='Retirement Pension Agent',
            description='Helps with retirement pension information and financial planning for retirement',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=RetirementPensionAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=RetirementPensionAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        # --8<-- [start:DefaultRequestHandler]
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=RetirementPensionAgentExecutor(),
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