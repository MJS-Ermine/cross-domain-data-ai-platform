"""
processors/finance_processor.py

金融資料處理器，負責清理與結構化爬取到的新聞資料，並更新回資料庫。
"""
from typing import Optional
import re
import logging
from database.database import SessionLocal, Article, init_db
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)

def clean_text(text: str) -> str:
    """簡單清理文本內容，移除 HTML 標籤、特殊字元等。"""
    # 移除 HTML 標籤
    text = re.sub(r"<.*?>", "", text)
    # 移除多餘空白
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def process_articles() -> None:
    """處理所有未處理過的金融新聞，並更新 processed_text_content。"""
    init_db()
    db: Session = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.processed_text_content == None).all()
        for art in articles:
            cleaned = clean_text(art.raw_text_content)
            art.processed_text_content = cleaned
            db.add(art)
            logging.info(f"已處理: {art.title}")
        db.commit()
    except Exception as e:
        logging.error(f"[資料處理錯誤] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    process_articles() 