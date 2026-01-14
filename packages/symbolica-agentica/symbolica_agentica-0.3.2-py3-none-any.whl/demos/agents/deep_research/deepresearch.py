#!/usr/bin/env -S S_M_BASE_URL=http://localhost:2345 uv run python3

import asyncio
import itertools
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import markdown
import validators
from exa_py import AsyncExa
from xhtml2pdf import pisa

from agentica.agent import Agent
from agentica.std.caption import CaptionLogger

exa = AsyncExa(api_key=os.getenv("EXA_API_KEY") or "20401de8-924f-431c-9294-327658c2d3c2")

CITATION_SP = """
You are a citation agent.

# Task
You must:
1. Review the research report line by line.
2. Identify which lines of the research report use information that could be from web search results.
3. List the web search results that were used in creating the research report.
3. For each of these lines, use the load_web_search_result function to load the web search result that was used.
4. Use the save_report function to save the research report to memory as a markdown file at the end.
5. Return saying you have finished.

# Rules
- You MUST use the list_web_search_results function to list the web search results that were used in creating the research report
- You MUST use the load_web_search_result function to load the web search results.
- You MUST use the save_report function to save the research report to memory at the end.
"""

LEAD_RESEARCHER_SP = """
You are a lead researcher.

# Task
You must:
1. Create a plan to research the user query.
2. Determine how many specialised subagents (with access to the web) are necessary, each with a different specific research task.
3. In separate REPL sessions, call each subagent to perform their research task.
4. Summarise the results of the subagents.
5. Return markdown that is the final research report.

# Rules
- Use the directory {directory}
- Do NOT need to check if the directory {directory} exists, it is local to the user therefore you.
- The planning process, subagents and final report MUST be done in SEPARATE REPL sessions.
- Do NOT construct the final report until you have run the subagents.
- Do NOT assign result in the REPL until planning, assigning subagents and returning the final report is complete.
- You MUST raise an AgentError if you cannot complete the task with what you have available.

## Planning
- You MUST write the plan yourself.
- You MUST write the plan before assigning subagents to tasks.
- You MUST break down the task into small individual tasks.

## Subagents
- You MUST assign each small individual task to a subagent.
- You MUST instruct subagents to use the web_search and save_used_web_search functions if the task requires it.
- Do NOT ask subagents to cite the web, instead instruct them to use the save_used_web_search function.
- Subagents MUST be assigned independent tasks.
- If after subagents have returned their findings more research is needed, you can assign more subagents to tasks.

## Final Report
- Do NOT write the final report yourself without running subagents to do so.
- You MUST load the plan it from memory before returning the final research report to check that you have followed the plan.
"""
SUBAGENT_SP = """
You are a helpful assistant.

# Task
You must:
1. Construct a list of things to search for using the web_search function.
2. Execute EACH web_search call in a separate REPL session.
3. For each search result, `print()` the content of each search result by accessing the SearchResult.content attribute
4. Identify which lines of content you are going to use in your report.
5. Use the save_used_web_search function to save the SearchResult to memory and include the lines of the content that you have used.
6. Condense the search results into a single report with what you have found.
7. Return the report by assigning `result` in the REPL.

# Rules
- Do NOT use the variable name `result` in the REPL until you have assigned it to the final report.
- You MUST use `print()` to print the content of each search result by accessing the SearchResult.content attribute.
- You MUST use the web_search function if instructed to do so OR if the task requires finding information.
- Do NOT assume that the web_search function will return the information you need, you must go through the content of each search result line by line by accessing the SearchResult.content attribute
- Do NOT assume which lines of content you are going to use in your report, you must go through the content of each search result line by line by accessing the SearchResult.content attribute
- If you cannot find any information, do NOT provide information yourself, instead raise an error for the lead researcher in the REPL.
- You MUST save the SearchResult of any research that you have used to memory and include the lines of the content that you have used.
- Assign `result` at the very end in a separate REPL session.
"""


def save_plan(plan: str, directory: str) -> None:
    """Save a research plan."""
    path = f"{directory}/plan.md"
    os.makedirs(directory, exist_ok=True)
    with open(path, "w") as f:
        _ = f.write(plan)


def load_plan(directory: str) -> str:
    """Load a research plan."""
    path = f"{directory}/plan.md"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Plan file {path} not made yet.")
    with open(path, "r") as f:
        return str(f.read())


def md_to_pdf(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    html_text = markdown.markdown(md_text)
    with open(output_path, "wb") as pdf_file:
        pisa.CreatePDF(html_text, dest=pdf_file)
    return output_path


@dataclass
class SearchResult:
    """
    Represents a single search result from the search engine.
    """

    title: str
    url: str
    content: str
    score: float | None = None
    lines_used: list[tuple[int, int]] | None = None

    def __post_init__(self):
        if not validators.url(self.url):
            raise ValueError("This is not a valid URL")

    def __repr__(self):
        return f"SearchResult(title={self.title}, score={self.score}, url={self.url}, ...)"

    def print_content_with_lines_numbers(self):
        """Print the content of the search result with the lines numbers that have been used."""
        for line_number, line in enumerate(self.content.split("\n"), start=1):
            print(f"{line_number}: {line}")

    def save(self, path: str, lines_used: list[tuple[int, int]]):
        """Save a web search result specifying which lines of the content have been used."""
        self.lines_used = lines_used
        if dir := os.path.dirname(path):
            os.makedirs(dir, exist_ok=True)
        with open(path, "w") as f:
            _ = f.write(json.dumps(self.__dict__))


async def web_search(query: str) -> list[SearchResult]:
    """Searches the web given a query, returning a list of SearchResults."""
    print(f"Searching the web for {query}")
    response = await exa.search_and_contents(
        query=query,
        num_results=2,
        text=True,  # Get text content in markdown format
    )
    results = []
    for result in response.results:
        # Exa automatically provides content in markdown format when text=True
        content = getattr(result, 'text', '<content missing/>')
        search_result = SearchResult(
            title=result.title or "<title missing/>",
            url=result.url,
            content=content,
            score=getattr(result, 'score', None),
        )
        results.append(search_result)
    return results


_id_gen = itertools.count(0)  # Backup ID gen when listeners are disabled.


class SubAgent:
    id: int
    n: int
    directory: str
    _brain: Agent

    # Seen by the lead researcher
    def __init__(self, directory: str):
        """Create a subagent that has access to the web."""
        self.n = 0
        self.directory = directory
        self._brain = Agent(
            model="openai:gpt-4.1",
            premise=SUBAGENT_SP,
            scope={
                "web_search": web_search,
                "SearchResult": SearchResult,
                "save_used_web_search": self._save_used_web_search,
            },
        )
        id = None
        if (listener := self._brain._listener) is not None:
            id = listener.logger.local_id
        if id is None:
            id = next(_id_gen)
        self.id = id

    # Seen by the lead researcher
    def __call__(self, task: str) -> str:
        """
        Run a subagent for a given task. The subagent will return its research, having saved the search results that it has used.
        """
        return asyncio.run(self._run(task))

    async def _run(self, task: str) -> str:
        print(f"Running web-search subagent ({self.id})")
        with CaptionLogger():
            result = await self._brain.call(str, task)
        return result

    def _get_path(self) -> str:
        self.n += 1
        return f"{self.directory}/subagent_{self.id}/result_{self.n}.json"

    def _save_used_web_search(
        self, search_result: SearchResult, lines_used: list[tuple[int, int]]
    ) -> None:
        """Save a SearchResult object as JSON."""
        search_result.save(self._get_path(), lines_used)


class CitationAgent:
    directory: str
    _brain: Agent

    def __init__(self, directory: str, system_prompt: str):
        self.directory = directory
        self._brain = Agent(
            model="openai:gpt-4.1",
            premise=system_prompt,
            scope={
                "list_web_search_results": self.list_web_search_results,
                "load_web_search_result": self.load_web_search_result,
                "save_report": self.save_report,
                "SearchResult": SearchResult,
            },
        )

    async def __call__(self, md_report: str) -> str:
        print("Running citation agent")
        return await self._brain.call(str, md_report)

    def load_web_search_result(self, path: str) -> SearchResult:
        """Load a search result queried by a subagent."""
        if not path.startswith(self.directory):
            raise ValueError(f"The file path must start with {self.directory}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Web search file {path} does not exist.")
        with open(path, "r") as f:
            return SearchResult(**json.loads(f.read()))

    def list_web_search_results(self) -> list[str]:
        """List all saved web search results queried by subagents."""
        directory_path = Path(self.directory)
        files: list[str] = []
        # Find all subagent_* directories
        for subagent_dir in directory_path.glob("subagent_*"):
            # Find result_<integer>.json files in each subagent directory
            if not subagent_dir.is_dir():
                continue
            for file in subagent_dir.iterdir():
                if (
                    file.is_file()
                    and file.suffix == '.json'
                    and re.match(r'^result_\d+$', file.stem)
                ):
                    files.append(str(file))
        return files

    def save_report(self, md_report: str) -> None:
        """Save a research report as markdown."""
        path = f"{self.directory}/plan.md"
        if dir := os.path.dirname(path):
            os.makedirs(dir, exist_ok=True)
        with open(path, "w") as f:
            _ = f.write(md_report)
        try:
            _ = md_to_pdf(path, f"{self.directory}/report.pdf")
        except Exception as e:
            print(f"Error converting markdown to PDF: {e}")


class DeepResearchSession:
    directory: str
    lr_system_prompt: str
    ca_system_prompt: str

    lead_researcher: Agent
    citation_agent: CitationAgent

    def __init__(
        self,
        directory: str,
        lr_system_prompt: str = LEAD_RESEARCHER_SP,
        ca_system_prompt: str = CITATION_SP,
    ):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory, exist_ok=True)
        self.lr_system_prompt = lr_system_prompt.format(directory=directory)
        self.ca_system_prompt = ca_system_prompt
        self.lead_researcher = Agent(
            premise=self.lr_system_prompt,
            model="openai:gpt-4.1",
            scope={
                "save_plan": save_plan,
                "load_plan": load_plan,
                "SubAgent": SubAgent,
            },
        )
        self.citation_agent = CitationAgent(
            directory=self.directory,
            system_prompt=self.ca_system_prompt,
        )

    async def __call__(self, query: str) -> str:
        """Run the deep research process and include citations at the end if it is generating a report for the first time."""
        with CaptionLogger():
            result = await self.lead_researcher.call(str, query)
            _ = await self.citation_agent(result)
        with open(f"{self.directory}/report.md", "w") as f:
            _ = f.write(result)
        _ = md_to_pdf(f"{self.directory}/report.md", f"{self.directory}/report.pdf")
        return (
            f"Check out the research report at {self.directory}/report.pdf. Ask me any questions!"
        )


if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))
    dr_session = DeepResearchSession("deep_research_test")
    result = asyncio.run(
        dr_session(
            "What are all of the companies in the US working on AI agents in 2025? make a list of at least 10. "
            + "For each, include the name, website and product, description of what they do, type of agents they build, and their vertical/industry."
        )
    )
    print(result)
