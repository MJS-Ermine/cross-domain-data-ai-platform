"""
data_sources/finance_scraper.py

金融新聞爬蟲模組，支援多來源設定，爬取標題、摘要、網址、發布日期，並存入資料庫。
"""
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from database.database import add_article, get_data_source_by_name, init_db, SessionLocal

logging.basicConfig(level=logging.INFO)

# 預設金融新聞來源（可擴充）
DEFAULT_SOURCES = [
    {
        "name": "Yahoo Finance TW",
        "domain_type": "finance",
        "base_url": "https://tw.stock.yahoo.com/news",
        "list_selector": "ul.List(n) li",
        "title_selector": "h3",
        "summary_selector": "p",
        "url_selector": "a",
        "date_selector": "time",
    },
]

def fetch_articles(source: Dict[str, str]) -> List[Dict[str, str]]:
    """爬取指定來源的新聞列表。"""
    articles = []
    try:
        resp = requests.get(source["base_url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(source["list_selector"])
        for item in items:
            title_tag = item.select_one(source["title_selector"])
            summary_tag = item.select_one(source["summary_selector"])
            url_tag = item.select_one(source["url_selector"])
            date_tag = item.select_one(source["date_selector"])
            if not (title_tag and url_tag):
                continue
            title = title_tag.get_text(strip=True)
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            url = url_tag["href"] if url_tag.has_attr("href") else ""
            if url and not url.startswith("http"):
                url = "https://tw.stock.yahoo.com" + url
            pub_date = None
            if date_tag and date_tag.has_attr("datetime"):
                try:
                    pub_date = datetime.fromisoformat(date_tag["datetime"])
                except Exception:
                    pub_date = None
            articles.append({
                "title": title,
                "summary": summary,
                "url": url,
                "publication_date": pub_date,
            })
    except Exception as e:
        logging.error(f"[爬蟲錯誤] 來源: {source['name']} - {e}")
    return articles

def scrape_and_store_all_sources() -> None:
    """爬取所有來源並存入資料庫。"""
    init_db()
    db = SessionLocal()
    for src in DEFAULT_SOURCES:
        # 可改為從資料庫讀取來源設定
        ds = get_data_source_by_name(db, src["name"])
        if not ds:
            # 若資料來源不存在則新增
            from database.database import add_data_source
            ds = add_data_source(db, src["name"], src["domain_type"], src["base_url"])
        articles = fetch_articles(src)
        for art in articles:
            try:
                add_article(
                    db,
                    source_id=ds.id,
                    title=art["title"],
                    raw_text_content=art["summary"],
                    url=art["url"],
                    publication_date=art["publication_date"],
                    metadata_json=None,
                )
            except Exception as e:
                logging.warning(f"[存儲失敗] {art['title']} - {e}")
    db.close()

if __name__ == "__main__":
    scrape_and_store_all_sources() 