import feedparser

NEWS_FEEDS = [
    ("한국경제", "https://www.hankyung.com/feed/finance"),
    ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy"),
    ("매일경제", "https://www.mk.co.kr/rss/30000001/"),
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
]

def fetch_financial_news(max_items=5):
    """
    여러 금융 뉴스 RSS에서 최신 뉴스를 수집해 리스트로 반환합니다.
    Args:
        max_items (int): 각 피드별로 최대 몇 개의 뉴스를 가져올지
    Returns:
        List[dict]: [{source, title, link} ...]
    """
    news_items = []
    for name, url in NEWS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            news_items.append({
                "source": name,
                "title": entry.title,
                "link": entry.link
            })
    return news_items 