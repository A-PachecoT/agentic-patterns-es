import arxiv
from datetime import datetime


def search_papers(query: str, max_results: int = 5) -> list:
    """Search arXiv for papers matching the query."""
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )

    results = []
    for paper in client.results(search):
        results.append(
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "summary": paper.summary,
                "url": paper.pdf_url,
                "published": paper.published,
                "paper_id": paper.entry_id.split("/")[-1],
                "categories": paper.categories,
            }
        )

    return results


def get_paper_by_id(paper_id: str) -> dict:
    """Get detailed information about a specific arXiv paper."""
    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[paper_id])
        paper = next(client.results(search))

        return {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "published": paper.published,
            "categories": paper.categories,
            "doi": paper.doi,
            "summary": paper.summary,
            "url": paper.pdf_url,
            "comment": paper.comment,
            "journal_ref": paper.journal_ref,
            "primary_category": paper.primary_category,
        }
    except Exception as e:
        return {"error": str(e)}
