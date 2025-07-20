import pickle
import os
import glob
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools.retriever import create_retriever_tool
from config.config import MODEL_CONFIG, EMBEDDING_CONFIG, VECTORSTORE_CONFIG
from typing import List, Dict
from langchain.schema import Document
from langchain_teddynote.retrievers import KiwiBM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.tools import BaseTool

def load_documents_from_pkl(filepath):
    """
    Pickle 파일에서 Langchain Document 리스트를 불러오는 함수

    Args:
        filepath: 원본 파일 경로 (예: path/to/filename.pdf)
    Returns:
        Langchain Document 객체 리스트
    """
    # 확장자 제거하고 절대 경로로 변환
    abs_path = os.path.abspath(filepath)
    base_path = os.path.splitext(abs_path)[0]
    pkl_path = f"{base_path}.pkl"

    with open(pkl_path, "rb") as f:
        documents = pickle.load(f)
    return documents

def load_documents_from_dir(dir_path):
    """
    지정된 디렉토리에서 모든 .pkl 파일을 찾아서 Langchain Document 리스트로 반환하는 함수

    Args:
        dir_path: 디렉토리 경로
    Returns:
        Langchain Document 객체 리스트
    """
    # extract_path 디렉토리에서 모든 .pkl 파일 찾기
    extract_path = dir_path
    pkl_files = glob.glob(str(Path(extract_path) / "**" / "*.pkl"), recursive=True)

    if not pkl_files:
        print("❌ extract_path에서 .pkl 파일을 찾을 수 없습니다.")
    else:
        # 모든 .pkl 파일에서 문서 로드
        all_documents = []
        for pkl_file in pkl_files:
            print(f"📄 {pkl_file} 파일 로드 중...")  # 한국어 코멘트
            documents = load_documents_from_pkl(pkl_file)
            all_documents.extend(documents)

        print(f"✅ 총 {len(all_documents)}개의 문서가 로드되었습니다.")
        return all_documents
    return []

def create_vectorstore(documents: List[Document]) -> FAISS:
    """문서를 벡터화하여 FAISS 벡터 스토어를 생성합니다.
    
    Args:
        documents: 벡터화할 문서 리스트
        
    Returns:
        생성된 FAISS 벡터 스토어
    """
    # 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings(**EMBEDDING_CONFIG)
    
    # FAISS 벡터 스토어 생성
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

def initialize_retriever_tool() -> List[BaseTool]:
    """FAISS 벡터 스토어를 초기화하고 리트리버 툴을 생성합니다.
    Returns:
        리트리버 툴 리스트
    """
    # bm25 retriever와 semantic retriever의 파라미터 설정
    vectorstore_path = VECTORSTORE_CONFIG["path"]

    bm25_k = VECTORSTORE_CONFIG["bm25_k"]
    semantic_k = VECTORSTORE_CONFIG["semantic_k"]
    bm25_weight = VECTORSTORE_CONFIG["bm25_weight"]
    semantic_weight = VECTORSTORE_CONFIG["semantic_weight"]

    # 벡터 스토어 로드
    documents = load_documents_from_dir(vectorstore_path)
    vector = create_vectorstore(documents)

    docs = vector.docstore._dict.values()
    texts = [doc.page_content for doc in docs]

    # 키워드 서치
    bm25_retriever = KiwiBM25Retriever.from_texts(texts)
    bm25_retriever.k = bm25_k 

    # 시멘틱 서치
    semantic_retriever = vector.as_retriever( search_kwargs={"k": semantic_k} )

    # 앙상블 리트리버 생성
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, semantic_retriever],
        weights=[bm25_weight, semantic_weight],  # 각 리트리버의 가중치 설정
        search_kwargs={"k": bm25_k + semantic_k},  # 최종 검색 결과 개수
    )

    # 리트리버 툴 생성
    retriever_tool = create_retriever_tool(
        ensemble_retriever,
        name="pdf_search",  # 도구의 이름을 입력합니다.
        description="use this tool to search financial information from the PDF document",  # 도구에 대한 설명을 자세히 기입해야 합니다!!
    )

    return retriever_tool

def save_vectorstore(vectorstore: FAISS, path: str):
    """벡터 스토어를 파일로 저장합니다.
    
    Args:
        vectorstore: 저장할 FAISS 벡터 스토어
        path: 저장할 파일 경로
    """
    vectorstore.save_local(path)

def load_vectorstore(path: str, embedding_model: str = "text-embedding-3-small") -> FAISS:
    """저장된 벡터 스토어를 로드합니다.
    
    Args:
        path: 벡터 스토어 파일 경로
        embedding_model: 사용할 임베딩 모델
        
    Returns:
        로드된 FAISS 벡터 스토어
    """
    # 임베딩 모델 초기화
    embeddings = OpenAIEmbeddings(
        model=embedding_model,
        openai_api_key=MODEL_CONFIG["openai_api_key"]
    )
    
    # 벡터 스토어 로드
    vectorstore = FAISS.load_local(path, embeddings)
    return vectorstore 