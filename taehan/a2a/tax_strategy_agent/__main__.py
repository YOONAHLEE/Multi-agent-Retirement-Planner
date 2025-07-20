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

from agent import TaxStrategyAgent
from agent_executor import TaxStrategyAgentExecutor


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10001)
def main(host, port):
    """Starts the Tax Strategy Agent server."""
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
            id='tax_strategy',
            name='Tax Strategy Tool',
            description='퇴직연금 및 IRP 관련 세액공제 정보와 연금 수령 방식에 따른 절세 전략을 안내합니다.',
            tags=['퇴직연금', '세액공제', '절세전략', '연금수령', 'DC형', 'DB형', '세금'],
            examples=[
                '퇴직연금 납입 시 받을 수 있는 세액공제 금액은?',
                'IRP에 추가 납입하면 세금 혜택이 어떻게 되나요?',
                '연금을 일시금으로 받는 것과 분할로 받는 것 중 어느 쪽이 절세에 유리한가요?',
                '연금 수령 방식에 따른 세금 계산 방법 알려줘',
                '퇴직연금 DC형과 DB형의 세금 처리 방식 차이를 설명해줘',
            ],
        )

        agent_card = AgentCard(
            name='Tax Strategy Agent',
            description='퇴직연금 및 IRP 납입과 연금 수령에 대한 절세 전략과 세액공제 정보를 제공하는 전문가 에이전트입니다. 벡터 데이터베이스 기반의 정보 검색도 지원합니다.',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=TaxStrategyAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=TaxStrategyAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )


        # --8<-- [start:DefaultRequestHandler]
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=TaxStrategyAgentExecutor(),
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