import requests

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class AcademicSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Academic research topic or question."
    )


class AcademicSearchTool(BaseTool):
    name: str = "Academic Literature Search"
    description: str = (
        "Search Crossref for relevant academic publications. "
        "Returns a small number of concise scholarly sources "
        "with title, authors, year, journal and DOI."
    )
    args_schema: type[BaseModel] = AcademicSearchInput

    def _run(self, query: str) -> str:

        try:

            response = requests.get(
                "https://api.crossref.org/works",
                params={
                    "query.bibliographic": query,
                    "rows": 4,
                    "select": (
                        "DOI,title,author,published,"
                        "container-title,type"
                    ),
                },
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

            items = data.get(
                "message",
                {}
            ).get(
                "items",
                []
            )

            if not items:
                return "No academic sources were found."

            results = []

            for index, item in enumerate(items[:4], 1):

                title = (
                    item.get("title", ["Unknown title"])[0]
                )

                authors = []

                for author in item.get("author", [])[:3]:

                    name = (
                        author.get("given", "")
                        + " "
                        + author.get("family", "")
                    ).strip()

                    if name:
                        authors.append(name)

                year = "Unknown"

                published = item.get(
                    "published",
                    {}
                ).get(
                    "date-parts",
                    []
                )

                if published and published[0]:
                    year = published[0][0]

                journal = (
                    item.get(
                        "container-title",
                        ["Unknown journal"]
                    )[0]
                )

                doi = item.get(
                    "DOI",
                    "No DOI"
                )

                results.append(
                    f"""
SOURCE {index}
Title: {title}
Authors: {", ".join(authors) if authors else "Unknown"}
Year: {year}
Journal: {journal}
DOI: https://doi.org/{doi}
""".strip()
                )

            return "\n\n".join(results)

        except Exception as e:

            return (
                "Academic search failed. "
                f"Reason: {str(e)}"
            )


class WebSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="General web research topic."
    )


class WebResearchTool(BaseTool):
    name: str = "Web Research Search"
    description: str = (
        "Search Wikipedia for concise background information. "
        "Returns a small number of relevant pages and URLs."
    )
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:

        try:

            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 4,
                    "format": "json",
                    "utf8": 1,
                },
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

            results = []

            for index, item in enumerate(
                data.get("query", {}).get(
                    "search",
                    []
                )[:4],
                1,
            ):

                title = item.get(
                    "title",
                    "Unknown"
                )

                snippet = item.get(
                    "snippet",
                    ""
                )

                # Remove HTML markup.
                snippet = (
                    snippet
                    .replace("<span class=\"searchmatch\">", "")
                    .replace("</span>", "")
                )

                url = (
                    "https://en.wikipedia.org/wiki/"
                    + title.replace(" ", "_")
                )

                results.append(
                    f"""
SOURCE {index}
Title: {title}
Summary: {snippet[:500]}
URL: {url}
""".strip()
                )

            if not results:
                return "No web sources were found."

            return "\n\n".join(results)

        except Exception as e:

            return (
                "Web search failed. "
                f"Reason: {str(e)}"
            )
