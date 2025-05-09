"""
analyzers/sentiment_analyzer.py

情感分析器，支援 Gemini API，將分析結果存入資料庫。
"""
from typing import Optional, Dict, Any
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from database.database import SessionLocal, Article, add_analysis, init_db
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = "請判斷下列新聞內容的情感傾向，僅回傳 '正面'、'負面' 或 '中性'。"


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """呼叫 Gemini API 進行情感分析。"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([SYSTEM_PROMPT, text])
        label = response.text.strip()
        return {"label": label, "raw": response.text}
    except Exception as e:
        logging.error(f"[情感分析錯誤] {e}")
        return {"label": "分析失敗", "error": str(e)}

def analyze_all_articles() -> None:
    """對所有已處理過但尚未分析的文章進行情感分析，並存入資料庫。"""
    init_db()
    db: Session = SessionLocal()
    try:
        articles = db.query(Article).filter(
            Article.processed_text_content != None
        ).all()
        for art in articles:
            # 檢查是否已分析過
            if any(a.analyzer_name == "sentiment_v1" for a in art.analyses):
                continue
            result = analyze_sentiment(art.processed_text_content)
            add_analysis(db, art.id, "sentiment_v1", result)
            logging.info(f"已分析: {art.title} -> {result['label']}")
    except Exception as e:
        logging.error(f"[批次情感分析錯誤] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_all_articles() 