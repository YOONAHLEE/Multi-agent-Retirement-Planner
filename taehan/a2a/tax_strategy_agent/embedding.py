import pickle
from typing import List, Dict
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from config.config import MODEL_CONFIG, EMBEDDING_CONFIG, VECTORSTORE_CONFIG
from langchain_community.vectorstores import OpenSearchVectorSearch
import os

current_path = os.getcwd()
print("현재 작업 경로:", current_path)

def load_documents(pkl_files: List[str]) -> List[Document]:
    """PKL 파일에서 문서를 로드합니다.
    
    Args:
        pkl_files: PKL 파일 경로 리스트
        
    Returns:
        로드된 문서 리스트
    """
    all_docs = []
    
    for pkl_file in pkl_files:
        # print("🔍 경로 확인:", os.path.abspath(pkl_file))
        # print("존재 여부:", os.path.exists(pkl_file))
        with open(pkl_file, 'rb') as f:
            docs = pickle.load(f)
            all_docs.extend(docs)
    
    print(f"총 문서 수: {len(all_docs)}개")
    return all_docs

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

def create_retrieval_chain(vectorstore: FAISS) -> RetrievalQA:
    """벡터 스토어를 기반으로 검색 체인을 생성합니다.
    
    Args:
        vectorstore: FAISS 벡터 스토어
        
    Returns:
        생성된 RetrievalQA 체인
    """
    # LLM 초기화
    llm = ChatOpenAI(**MODEL_CONFIG)
    
    # RetrievalQA 체인 생성
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever()
    )
    
    return qa_chain

def initialize_vectorstores() -> Dict[str, RetrievalQA]:
    """모든 벡터 스토어를 초기화하고 검색 체인을 생성합니다.
    
    Returns:
        벡터 스토어 ID를 키로 하는 RetrievalQA 체인 딕셔너리
    """
    qa_chains = {}
    
    for store_id, config in VECTORSTORE_CONFIG.items():
        # 문서 로드
        documents = load_documents(config["pkl_files"])
        
        # 벡터 스토어 생성
        vectorstore = create_vectorstore(documents)
        
        # 검색 체인 생성
        qa_chain = create_retrieval_chain(vectorstore)
        
        qa_chains[store_id] = qa_chain
    
    return qa_chains

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