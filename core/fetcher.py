import feedparser
from urllib.parse import quote


def fetch_papers(query, start=0, max_results=5):
    query_encoded = quote(query)

    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{query_encoded}"
        f"&start={start}"
        f"&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )

    feed = feedparser.parse(url)

    papers = []
    for entry in feed.entries:
        papers.append({
            "id": entry.id,
            "title": entry.title,
            "summary": entry.summary,
            "pdf": entry.link.replace("abs", "pdf")
        })

    return papers