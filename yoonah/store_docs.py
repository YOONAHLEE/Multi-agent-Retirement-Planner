import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings 
# from langchain.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain.document_loaders import PyPDFLoader, WebBaseLoader

# from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
# from langchain.schema import Document
from langchain_core.documents import Document as LangchainDocument
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict, Any
from langgraph.graph import END, StateGraph
from datetime import datetime, timedelta
import re
from termcolor import colored
import pandas as pd
import holidays


load_dotenv("openai.env")

# 모델 세팅
# llm = ChatOpenAI(model="gpt-4", temperature=0.3)
llm = ChatGroq(model='llama-3.3-70b-versatile')
# embedding_model = OllamaEmbeddings(model='bge-m3')
vectorstore_path = "vectordb"
embedding_model = OpenAIEmbeddings()


def get_previous_business_day(date: datetime) -> datetime:
    """Get the previous business day, skipping weekends and Korean holidays"""
    kr_holidays = holidays.KR()
    
    while True:
        date = date - timedelta(days=1)
        # Check if it's a weekday and not a holiday
        if date.weekday() < 5 and date not in kr_holidays:
            return date

def get_target_date() -> tuple[datetime, str]:
    """Get the target date for data retrieval, considering weekends and holidays"""
    current_date = datetime.now()
    kr_holidays = holidays.KR()
    
    # Check if today is a weekend or holiday
    if current_date.weekday() >= 5 or current_date in kr_holidays:
        print(f"오늘은 {'주말' if current_date.weekday() >= 5 else '공휴일'}입니다.")
        target_date = get_previous_business_day(current_date)
        print(f"이전 영업일인 {target_date.strftime('%Y-%m-%d')} 데이터를 가져옵니다.")
    else:
        target_date = current_date
        print(f"오늘({target_date.strftime('%Y-%m-%d')})은 영업일입니다.")
    
    # Format date for directory
    date_str = target_date.strftime("%y%m%d")
    return target_date, date_str

#  웹 문서 수집 함수
def fetch_html_content(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text

def parse_naver_blog(url: str) -> LangchainDocument:
    html = fetch_html_content(url)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return LangchainDocument(page_content=text, metadata={"source": url})

def parse_naver_pdf(url: str) -> LangchainDocument:
    pdf_url = url.split("url=")[-1]
    pdf_url = requests.utils.unquote(pdf_url)
    pdf_path = "temp.pdf"
    with open(pdf_path, "wb") as f:
        f.write(requests.get(pdf_url).content)
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    return docs[0]

def get_documents_from_links(html_links):
    all_docs = []
    for url in html_links:
        print(f"Parsing {url}")
        if "pdf?url=" in url:
            all_docs.append(parse_naver_pdf(url))
        else:
            all_docs.append(parse_naver_blog(url))
    return all_docs

#   임베딩 및 벡터 저장소 구축
# def build_vectorstore(documents):
#     splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
#     chunks = splitter.split_documents(documents)
#     vectorstore = Chroma.from_documents(chunks, embeddings_model)
    
#     # Check if the vectorstore is storing the embeddings correctly
#     if vectorstore:
#         print(f"Vectorstore created with {len(chunks)} chunks.")
#         sample_chunk = chunks[0].page_content if chunks else "No chunks available"
#         print(f"Sample chunk: {sample_chunk[:200]}...")  # Print first 200 characters of a sample chunk
#     else:
#         print("Failed to create vectorstore.")
    
#     return vectorstore

def build_vectorstore(documents, persist_dir):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir  # 저장 위치 설정
    )
    try:
        vectorstore.persist()  
    except Exception as e:
        print(f"Error during persistence: {e}")
        return None
    
    print(f"✅ Vectorstore created and saved with {len(chunks)} chunks.")
    return vectorstore

# 상태 정의
# class ReportState(TypedDict):
#     query: str
#     documents: List[LangchainDocument]
#     analysis: str
#     report_sections: Dict[str, str]
#     final_report: str
#     pdf_path: str

def create_date_directory(date_str):
    """날짜별 디렉토리 생성"""
    base_dir = "data"
    date_dir = os.path.join(base_dir, date_str)
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    return date_dir

def fetch_daily_reports(target_date, date_str):
    """네이버 증권 데일리 리포트 수집"""
    # base_urls = [
    #     "https://finance.naver.com/research/debenture_list.naver",  # 채권 리포트
    #     "https://finance.naver.com/research/economy_list.naver",    # 경제 리포트
    #     "https://finance.naver.com/research/market_info_list.naver", # 시장정보 리포트
    #     "https://finance.naver.com/research/invest_list.naver"      # 투자 리포트
    # ]
    base_url_list = [
        "https://finance.naver.com/research/market_info_list.naver", # daily report, 
        "https://finance.naver.com/research/invest_list.naver", # 투자 리포트 
        "https://finance.naver.com/research/economy_list.naver" # 경제 리포트 
    ]
    date_dir = create_date_directory(date_str)

    headers = {'User-Agent': 'Mozilla/5.0'}

    for base_url in base_url_list:
        all_reports = []
        for page in range(1, 3):
                
            print(f"🔎 Scraping page {page}...")
            res = requests.get(f"{base_url}?page={page}", headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")

            table = soup.find("table", class_="type_1")
            # print(table)
            rows = table.find_all("tr")[2:]

            for row in rows:
                cols = row.find_all("td")
                print(colored(f"cols: {cols}", "red"))

                pdf_tag = row.select_one('td.file a[href*=".pdf"]')
                print(colored(f"pdf tag: {pdf_tag}", "yellow"))
                if pdf_tag and 'href' in pdf_tag.attrs:
                    pdf_url = pdf_tag['href']
                else:
                    print("Cannot find related pdf path")
                    continue
                
                all_reports.append({
                    "title": cols[0].get_text(strip=True) if cols else "Unknown", 
                    "date": cols[3].get_text(strip=True) if len(cols) > 3 else "Unknown",
                    "pdf_url": pdf_url
                })

        # Convert to DataFrame
        df = pd.DataFrame(all_reports)
        print(df)
        
        # Set pandas display options to show full URLs
        pd.set_option('display.max_colwidth', None)  # Show full content of columns
        pd.set_option('display.width', None)  # Use full terminal width
        pd.set_option('display.max_columns', None)  # Show all columns
        
        print("\n=== Full URLs ===")
        print(df)

        
        for each in all_reports:
            if each["date"] == today:
                doc_title = re.sub(r'[^\w\-_\. ]', '_', each['title'])
                print(each['title'], doc_title)
                pdf_filename = f"{doc_title}.pdf"
                pdf_path = os.path.join(date_dir, pdf_filename)
                download_pdf(each['pdf_url'], pdf_path)
            
    

def download_pdf(url, save_path):
    """PDF 파일 다운로드"""
    try:
        response = requests.get(url, stream=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"PDF 다운로드 중 오류 발생: {str(e)}")
        return False

# def retrieve_documents(state: ReportState) -> ReportState:
#     print("Step 1: 관련 문서 검색 중...")
#     current_date = datetime.now()
    
#     # 주말인 경우 금요일 데이터를 가져옴
#     if current_date.weekday() >= 5:  # 5: Saturday, 6: Sunday
#         days_to_subtract = current_date.weekday() - 4  # 금요일(4)까지의 일수 계산
#         target_date = current_date - timedelta(days=days_to_subtract)
#         print(f"주말이므로 {target_date.strftime('%Y-%m-%d')} 금요일 데이터를 가져옵니다.")
#     else:
#         target_date = current_date
    
#     date_str = target_date.strftime("%y%m%d")  # YYMMDD 형식
#     documents = process_daily_reports(date_str)
#     print(f"검색된 문서 수: {len(documents)}")
#     return {**state, "documents": documents}


# def create_report_graph():
#     workflow = StateGraph(ReportState)
#     # 노드 추가
#     workflow.add_node("retrieve", retrieve_documents)
#     # 엣지 설정
#     workflow.set_entry_point("retrieve")
#     workflow.add_edge("retrieve", END)
#     return workflow.compile()


if __name__ == "__main__":



    # 보고서 생성 시작
    # graph = create_report_graph()
    # query = "최신 시장 동향과 투자 기회에 대한 종합적인 분석 보고서를 작성해주세요."
    # initial_state = ReportState({
    #     "query": query,
    #     "documents": [],
    #     "analysis": "",
    #     "report_sections": {},
    #     "final_report": "",
    #     "pdf_path": ""
    # })
    # result = graph.invoke(initial_state)

    # Today's date in 'yy.mm.dd' format (matches the Naver page format)
    # today = datetime.now().strftime('%y.%m.%d')
    
    # Get target date considering holidays
    today, date_str = get_target_date()
    today = today.strftime('%y.%m.%d')
    
    fetch_daily_reports(today, date_str)






