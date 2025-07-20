from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declarative_base
from config.config import settings

# PostgreSQL 데이터베이스 URL
DATABASE_URL = settings.DATABASE_URL

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 이 클래스를 상속받음)
Base = declarative_base()

# DB 세션 종속성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)