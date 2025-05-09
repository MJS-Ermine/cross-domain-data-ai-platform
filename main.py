"""
main.py

主流程控制腳本，串接爬蟲、資料處理、情感分析三大模組。
"""
import logging
from data_sources.finance_scraper import scrape_and_store_all_sources
from processors.finance_processor import process_articles
from analyzers.sentiment_analyzer import analyze_all_articles

logging.basicConfig(level=logging.INFO)

def main() -> None:
    """執行端到端金融新聞蒐集、處理、分析流程。"""
    logging.info("[1/3] 開始爬取金融新聞...")
    scrape_and_store_all_sources()
    logging.info("[2/3] 開始資料清理...")
    process_articles()
    logging.info("[3/3] 開始情感分析...")
    analyze_all_articles()
    logging.info("流程完成！")

if __name__ == "__main__":
    main()
