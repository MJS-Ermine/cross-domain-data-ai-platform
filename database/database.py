"""
database/database.py

資料庫模組，負責初始化連線、定義資料表（DataSource, Article, Analysis），並提供基本 CRUD 操作。
"""
from typing import Optional, Any, Dict
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.types import JSON
from datetime import datetime
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

DB_URL: str = os.getenv("DB_URL", "sqlite:///database.db")

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class DataSource(Base):
    """資料來源表"""
    __tablename__ = "data_sources"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(128), nullable=False)
    domain_type: str = Column(String(32), nullable=False)  # 例：finance, legal
    base_url: str = Column(String(256), nullable=False)
    articles = relationship("Article", back_populates="source")

class Article(Base):
    """文章表"""
    __tablename__ = "articles"
    id: int = Column(Integer, primary_key=True, index=True)
    source_id: int = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    title: str = Column(String(256), nullable=False)
    raw_text_content: str = Column(Text, nullable=False)
    processed_text_content: Optional[str] = Column(Text)
    url: str = Column(String(512), nullable=False, unique=True)
    publication_date: Optional[datetime] = Column(DateTime)
    scraped_at: datetime = Column(DateTime, default=datetime.utcnow)
    metadata_json: Optional[Dict[str, Any]] = Column(JSON)
    source = relationship("DataSource", back_populates="articles")
    analyses = relationship("Analysis", back_populates="article")

class Analysis(Base):
    """分析結果表"""
    __tablename__ = "analyses"
    id: int = Column(Integer, primary_key=True, index=True)
    article_id: int = Column(Integer, ForeignKey("articles.id"), nullable=False)
    analyzer_name: str = Column(String(64), nullable=False)  # 例：sentiment_v1
    result_json: Dict[str, Any] = Column(JSON, nullable=False)
    analyzed_at: datetime = Column(DateTime, default=datetime.utcnow)
    article = relationship("Article", back_populates="analyses")

def init_db() -> None:
    """初始化資料庫，建立所有資料表。"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """取得資料庫 Session 實例。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 範例 CRUD 操作

def add_data_source(db: Session, name: str, domain_type: str, base_url: str) -> DataSource:
    """新增資料來源。"""
    ds = DataSource(name=name, domain_type=domain_type, base_url=base_url)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds

def get_data_source_by_name(db: Session, name: str) -> Optional[DataSource]:
    """依名稱查詢資料來源。"""
    return db.query(DataSource).filter(DataSource.name == name).first()

def add_article(db: Session, source_id: int, title: str, raw_text_content: str, url: str, publication_date: Optional[datetime], metadata_json: Optional[Dict[str, Any]] = None) -> Article:
    """新增文章。"""
    article = Article(
        source_id=source_id,
        title=title,
        raw_text_content=raw_text_content,
        url=url,
        publication_date=publication_date,
        metadata_json=metadata_json,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def add_analysis(db: Session, article_id: int, analyzer_name: str, result_json: Dict[str, Any]) -> Analysis:
    """新增分析結果。"""
    analysis = Analysis(
        article_id=article_id,
        analyzer_name=analyzer_name,
        result_json=result_json,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis 