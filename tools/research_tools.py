import requests
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class AcademicSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Academic research topic or question to search."
    )


class AcademicSearchTool(BaseTool):
    name: str = "academic_literature_search"

    description: str = (
        "Search Crossref for academic and scholarly publications. "
        "Use this when you need peer-reviewed papers, journal articles, "
        "DOIs, publication years, authors, or scholarly evidence."
    )

    args_schema: Type[BaseModel] = AcademicSearchInput

    def _run(self, query: str) -> str:

        try:
            response = requests.get(
                "https://api.crossref.org/works",
                params={
                    "query.bibliographic": query,
                    "rows": 6,
                    "select": (
                        "title,author,published,DOI,"
                        "container-title,type"
                    ),
                },
                headers={
                    "User-Agent": (
                        "ResearchLabAI/1.0 "
                        "(mailto:research@example.com)"
                    )
                },
                timeout=20,
            )

            response.raise_for_status()

            items = response.json()["message"]["items"]

            if not items:
                return "No academic publications were found."

            results = []

            for index, item in enumerate(items, start=1):

                title = (
                    item.get("title", ["Untitled"])[0]
                )

                authors = []

                for author in item.get("author", [])[:5]:
                    given = author.get("given", "")
                    family = author.get("family", "")

                    name = f"{given} {family}".strip()

                    if name:
                        authors.append(name)

                date_parts = (
                    item.get("published", {})
                    .get("date-parts", [[]])[0]
                )

                year = (
                    date_parts[0]
                    if date_parts
                    else "Unknown"
                )

                doi = item.get("DOI", "")

                journal = (
                    item.get("container-title", [""])[0]
                )

                doi_url = (
                    f"https://doi.org/{doi}"
                    if doi
                    else "No DOI available"
                )

                results.append(
                    f"""
SOURCE {index}

Title: {title}

Authors: {", ".join(authors) or "Not listed"}

Year: {year}

Journal: {journal or "Not listed"}

DOI: {doi_url}
"""
                )

            return "\n".join(results)

        except Exception as exc:
            return f"Academic search failed: {exc}"


class WebSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="General research topic to search."
    )


class WebResearchTool(BaseTool):
    name: str = "web_research_search"

    description: str = (
        "Search Wikipedia's public knowledge API for reliable general "
        "background information and source pages. Use this for concepts, "
        "organizations, historical background, and broad research context."
    )

    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:

        try:
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 6,
                    "format": "json",
                    "utf8": 1,
                },
                headers={
                    "User-Agent": "ResearchLabAI/1.0"
                },
                timeout=20,
            )

            response.raise_for_status()

            results = response.json()["query"]["search"]

            if not results:
                return "No web sources were found."

            output = []

            for index, item in enumerate(results, start=1):

                title = item["title"]

                snippet = (
                    item["snippet"]
                    .replace("<span class=\"searchmatch\">", "")
                    .replace("</span>", "")
                )

                url = (
                    "https://en.wikipedia.org/wiki/"
                    + title.replace(" ", "_")
                )

                output.append(
                    f"""
SOURCE {index}

Title: {title}

Summary: {snippet}

URL: {url}
"""
                )

            return "\n".join(output)

        except Exception as exc:
            return f"Web research failed: {exc}"
