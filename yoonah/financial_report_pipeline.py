# advanced_financial_rag_pipeline.ipynb

# 📌 Step 1: 라이브러리 임포트 및 설정
from datetime import date
from langchain_upstage import UpstageDocumentParseLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.chains.summarize import load_summarize_chain
from langchain.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langchain_core.output_parsers import StrOutputParser
import os
import glob
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from typing import Annotated, List, Literal, TypedDict
from store_docs import get_target_date
from langchain_core.runnables.graph_mermaid import MermaidDrawMethod
# from langchain_openrouter import ChatOpenRouter
import warnings
from termcolor import colored
from typing import Optional, ClassVar

from langchain_core.utils.utils import secret_from_env
from pydantic import Field, SecretStr


warnings.filterwarnings("ignore")
# API 키 및 디렉토리 설정
load_dotenv("openai.env")

TODAY = date.today().isoformat()
SUMMARY_CACHE_PATH = "cache_db"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 요약 문서가 없다면 새로 생성하고 저장
class ChatOpenRouter(ChatOpenAI):
    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )
    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        openai_api_key = (
            openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=openai_api_key,
            **kwargs
        )

llm = ChatOpenRouter(
    model_name="anthropic/claude-3.7-sonnet:thinking"
)

summarize_chain = load_summarize_chain(llm, chain_type="map_reduce")

### Define State
# class PipelineState:
#     def __init__(self):
#         self.date = date.today().isoformat() # 2025-05-07
#         self.last_business_day = ""
#         self.query = ""
#         self.documents = []
#         self.doc_summary = ""
#         self.web_summary = ""
#         self.final_output = ""
#         self.db_path = "cache_db"


class PipelineState(TypedDict, total=False):
    date: str
    last_business_day: str
    query: str
    documents: List[Document]
    doc_summary_chunks: List[str]
    doc_summary: str
    web_summary: str
    final_output: str
    db_path: str


### Define Nodes
def load_docs(state):
    state["date"] = date.today().isoformat()
    business_day, business_day_str = get_target_date()
    state["last_business_day"] = business_day_str
    state["db_path"] = SUMMARY_CACHE_PATH
    
    print(state)

    if not os.path.exists(state["db_path"]):
        os.makedirs(state["db_path"])
    
    # Chroma에서 해당 날짜 컬렉션 로드 또는 생성
    vectordb = Chroma(
        collection_name=business_day_str,
        embedding_function=embeddings,
        persist_directory=state["db_path"])
    
    # 컬렉션에 문서가 존재하는지 확인
    docs = vectordb.get()
    if len(docs["ids"]) > 0 :# if collecion exists
        # load documents
        print(f"Found {len(docs['ids'])} documents in the database")
        # Convert dictionary to list of Document objects
        print("db stores documents")
        documents = [
            Document(
                page_content=doc,
                metadata=meta
            ) for doc, meta in zip(docs["documents"], docs["metadatas"])
        ]
        state["documents"] = documents

    else:
        # load documents
        path = f"data/{state['last_business_day']}"
        if not os.path.exists(path):
            from store_docs import fetch_daily_reports
            fetch_daily_reports(business_day.strftime('%y.%m.%d'), business_day_str)
        files = glob.glob(f"{path}/**.pdf", recursive=True)
        parser = UpstageDocumentParseLoader(
            files, output_format='markdown', 
            coordinates=False) 
        documents = parser.load()
        print(f"Found {len(documents)} documents to process")
        
        # 메타데이터에서 base64 인코딩된 이미지 데이터 제거
        # for doc in documents:
        #     if doc.metadata:
        #         # base64로 시작하는 키-값 쌍 제거
        #         doc.metadata = {k: v for k, v in doc.metadata.items() 
        #                       if not isinstance(v, str) or not v.startswith('/9j/')}
        
        state["documents"] = documents
        vectordb.add_documents(documents)  # Save documents into vector DB
    return state
# 조건 분기: 쿼리에 "보고서" 포함 여부
def check_query_type(state: PipelineState) -> str:
    """
    Determine which search path to take based on query content
    """
    if "보고서" in state["query"]:
        return "search_general_web"
    else:
        return "search_certain_web"

# 2. Summarize documents
def summarize_documents(state: PipelineState) -> PipelineState:

    map_prompt = ChatPromptTemplate.from_template("""
    다음의 금융 문서를 금융 시장 전망, 시황, 핵심 지표 및 수치, 투자 전략 및 시사점 중심으로 요약해주세요. 
    금융 문서:
    {context}
    """)
    reduce_template = ChatPromptTemplate.from_template("""
    다음은 여러 금융 문서 블록들의 중간 요약입니다. 이 내용을 바탕으로 전체 보고서의 최종 요약을 작성해주세요.

    요구사항:
    - 중복된 표현은 피하되, **중요한 정보는 생략하지 말고 포함**해주세요.
    - 보고서 형식으로 항목별로 정리해주세요.
    - 특히 아래 4가지 주제에 따라 구분하여 통찰력 있게 기술해주세요:

    1. 시장 전망 (경제 전체의 방향, 거시 지표 해석 등)
    2. 시황 요약 (최근 시장 동향, 주요 뉴스 및 이벤트 요약)
    3. 핵심 지표 및 수치 (금리, 환율, CPI 등 중요 지표 변화 포함)
    4. 투자 전략 및 시사점 (투자자에게 유용한 전략 및 관찰 포인트)

    중간 요약 내용:
    {context}
    """)

    # map: sumarize each document
    print(state)
    map_chain = map_prompt | llm | StrOutputParser()
    mapped_summaries = [map_chain.invoke({"context": doc.page_content}) for doc in state["documents"]]
    # optionally log intermediate summaries 
    state["doc_summary_chunks"] = mapped_summaries
    print(mapped_summaries)
    # reduce: aggregate final summary 
    reduced_input = "\n\n".join(mapped_summaries)
    print(f'reduced_input is {reduced_input}')
    reduce_chain = reduce_template | llm | StrOutputParser()
    doc_summary = reduce_chain.invoke({"context": reduced_input})
    state["doc_summary"] = doc_summary

    filename = f"reports/middle_report_doc_summary_{state['date']}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {state['date']} 리포트\n\n{doc_summary}")
    print(f"[✓] {filename} 저장 완료")

    return state

# 3. Tavily Web Search for current insights
def search_general_web(state: PipelineState) -> PipelineState:

    search_query = "Today's global market performance by region US, Europe, Asia, and Korea; index, currency, oil, gold, central bank"
    tavily_tool = TavilySearchResults(k=5)
    results = tavily_tool.invoke({"query": search_query})
    web_results = "\n".join([r["content"] for r in results])

    prompt = f"""
    다음은 오늘의 금융 시장 요약 자료입니다:

    {web_results}

    금융 시장 전망, 글로벌 시황, 주요 이슈 및 영향에 대해 통찰력있고, 명확하게 요약해주세요.
    """
    summary = llm.invoke(prompt).content
    filename = f"reports/middle_report_general_search_{state['date']}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {state['date']} 리포트\n\n{summary}")
    print(f"[✓] {filename} 저장 완료")
    # 요약 출력
    print("\n[요약 결과]")
    state["web_summary"] = summary
    return state 


def search_certain_web(state: PipelineState) -> PipelineState:
    
    search_query = f'{state["query"]}  시황 {state["date"]}'
    tavily_tool = TavilySearchResults(k=2)
    results = tavily_tool.invoke({"query": search_query})
    
    prompt = f"""
    다음은 '{search_query}'에 대한 웹 기사 요약 자료입니다:
    {results}
    {search_query} 전망, 시황, 주요 이슈 및 영향에 대해 요약해주세요.
    """
    summary = llm.invoke(prompt).content
    state["web_summary"] = summary
    # # 요약 출력
    # print("\n[요약 결과]")
    # print(summary)
    filename = f"reports/middle_report_{search_query[:10]}_{state['date']}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {state['date']} 리포트\n\n{summary}")
    print(f"[✓] {filename} 저장 완료")
    return state 


def merge_outputs(state: PipelineState) -> PipelineState:
    merge_prompt = PromptTemplate.from_template("""
당신은 초보 투자자도 이해할 수 있는 수준에서 분석 내용을 정리해주는 **금융 분석가**입니다. 
다음 보고서 기존 요약과 실시간 검색 요약을 바탕으로 **종합적이고 쉽고 명확한** 한국 투자자 전용 일일 금융 보고서를 작성해주세요.

기존 요약:
{doc_summary}

실시간 검색 요약:
{web_summary}

⚠️ 작성 시 유의사항:
- 전문 용어는 가능한 쉬운 표현으로 바꾸거나 괄호 안에 설명을 추가해주세요.
- 숫자나 지표가 나오면 반드시 의미를 해석해서 설명해주세요 (예: "금리가 3%로 상승 → 대출 이자 부담 증가로 소비 위축 가능성").

📊 다음 형식으로 작성해주세요:

# 오늘의 금융 레포트
                                                
### 1. 금융 시장 동향
- **주요 지표 및 추세**: (예: 소비자물가지수 상승률, 에너지 가격, 금리 변화 등)
- **소비 심리 분석**: 최근 소비자들이 어떻게 반응하고 있는지
- **시장 동향**: 전체적인 증시/채권/환율 흐름 요약
                                                                                                
---

### 2. 투자 전략 시사점

 **기회 요인 (Bullish signals)**  
- 주요 기회 요인 1  
- 주요 기회 요인 2   
- 주요 기회 요인 3 

 **리스크 요인 (Bearish signals)**  
- 주요 리스크 1  
- 주요 리스크 2   
- 주요 리스크 3 

---

### 3. 투자 Action Point (표 형식)

| 구분        | 투자 아이디어                   | 초보자를 위한 설명 및 분석 근거              |
|-------------|------------------------------|-------------------------------------------|
| 채권        | 구체적인 채권 투자 전략        | 금리 흐름, 채권 수익률 등과 연관지어 설명   |
| 주식        | 구체적인 주식 투자 전략        | 산업 동향, 뉴스 기반 전망 포함  |
| 섹터 회피    | 피해야 할 업종 또는 테마        | 악재 요인, 실적 부진 등 이유 포함      |
| ETF 제안    | 추천 ETF 및 이유              | 초보자 기준으로 리스크/분산 설명 포함   |
| 환율 전략    | 환율과 관련된 전략              | 수출/수입 기업에 어떤 영향을 줄지 설명   |

---

### 4.  전략적 제언 (쉽게 정리된 포트폴리오 조언)
- **시장 전망 요약**: 앞으로 몇 주간 어떤 흐름이 예상되는지
- **포트폴리오 구성 방향**: 예: "채권 60% + 주식 30% + 금 5% + 비트코인 5% 비중 추천"
- **주의해야 할 점**: 불확실성 요인, 정책 발표 일정 등
                                        
""")
    prompt_input = merge_prompt.format(
        doc_summary=state["doc_summary"],
        web_summary=state["web_summary"]
    )
    output = llm.invoke(prompt_input).content
    state["final_output"] = output
    return state

# 6. Save output to PDF and .md
def save_output(state: PipelineState) -> PipelineState:
    with open(f"reports/final_report_{state['date']}.md", "w", encoding="utf-8") as f:
        f.write(state["final_output"])
    return state

# LangGraph 설정

builder = StateGraph(PipelineState)
# Register all nodes
builder.add_node("load_docs", load_docs)
builder.add_node("docs_summarize", summarize_documents)
builder.add_node("search_general_web", search_general_web)
builder.add_node("search_certain_web", search_certain_web)
builder.add_node("merge", merge_outputs)
builder.add_node("save", save_output)

# Flow control
builder.add_edge(START, "load_docs")
builder.add_edge("load_docs", "docs_summarize")
# builder.add_edge("docs_summarize", "check_query_type")

# Conditional routing based on query type
builder.add_conditional_edges(
    "docs_summarize",
    check_query_type,
    {
        "search_general_web": "search_general_web",
        "search_certain_web": "search_certain_web"
    }
)

# Common path after search
builder.add_edge("search_general_web", "merge")
builder.add_edge("search_certain_web", "merge")
builder.add_edge("merge", "save")
builder.add_edge("save", END)

# Compile app
adaptive_rag = builder.compile()


if __name__ == "__main__":

    # Initialize state with required keys
    inputs = {
        "date": date.today().isoformat(),
        "query": "오늘의 금융 보고서를 작성해주세요",
        "documents": [],  # Initialize empty documents list
        "doc_summary_chunks": [],
        "doc_summary": "",
        "web_summary": "",
        "final_output": "",
        "db_path": SUMMARY_CACHE_PATH
    }

    final_output = adaptive_rag.invoke(inputs)


    # Visualize graph
    # png_graph = adaptive_rag.get_graph().draw_mermaid_png()
    png_graph = adaptive_rag.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.PYPPETEER
    )

    with open("graph.png", "wb") as f:
        f.write(png_graph)



