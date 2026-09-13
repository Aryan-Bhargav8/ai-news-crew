import os
import re
from crewai import Agent, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
load_dotenv()

# Patterns that could be used to abuse Serper's search directives for SSRF /
# internal network scanning (e.g. site:localhost, site:192.168.x.x, ports).
_SSRF_PATTERNS = [
    re.compile(r"site\s*:", re.IGNORECASE),
    re.compile(r"\b(localhost|127\.0\.0\.1|0\.0\.0\.0)\b", re.IGNORECASE),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r":\d{2,5}\b"),
]


class SafeSerperDevTool(SerperDevTool):
    """SerperDevTool wrapper that strips SSRF-prone search directives
    (e.g. site:, internal IPs/hosts, explicit ports) from the query."""

    def _run(self, **kwargs):
        query = kwargs.get("search_query") or kwargs.get("query") or ""
        for pattern in _SSRF_PATTERNS:
            query = pattern.sub("", query)
        if "search_query" in kwargs:
            kwargs["search_query"] = query.strip()
        elif "query" in kwargs:
            kwargs["query"] = query.strip()
        return super()._run(**kwargs)


# Patterns commonly used to hijack an LLM's behaviour via injected text
# (e.g. through user-controlled template placeholders such as {topic}).
_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\bignore\s+(all\s+)?(previous|above)\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"\bsystem\s*prompt\b", re.IGNORECASE),
    re.compile(r"\bnew\s+instructions?\b", re.IGNORECASE),
]


def _sanitize_interpolated_value(value):
    """Strip newlines/control characters and neutralize common role-switching
    or instruction-override phrases from user-supplied values that get
    interpolated into agent prompts (e.g. {topic})."""
    if not isinstance(value, str):
        return value
    sanitized = re.sub(r"[\r\n\t]+", " ", value)
    for pattern in _PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[filtered]", sanitized)
    return sanitized.strip()


class SafeAgent(Agent):
    """Agent subclass that sanitizes inputs before they are interpolated into
    role/goal/backstory templates, mitigating prompt injection via untrusted
    placeholder values such as {topic}."""

    def interpolate_inputs(self, inputs):
        if isinstance(inputs, dict):
            inputs = {k: _sanitize_interpolated_value(v) for k, v in inputs.items()}
        return super().interpolate_inputs(inputs)


GROQ_API_KEY = os.getenv('GROQ_API_KEY')
MODEL = os.getenv("MODEL")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY or not SERPER_API_KEY or not MODEL:
    raise RuntimeError(
        "Missing required credentials: ensure GROQ_API_KEY, SERPER_API_KEY and "
        "MODEL are set via a secrets manager or secure environment, not committed to source control."
    )

llm = LLM(
    model=MODEL,
    api_key=GROQ_API_KEY,
    temperature=0,
    reasoning_effort="medium",
)


researcher = SafeAgent(
    role = "Senior Data Researcher",
    goal = "Uncover cutting-edge developments in {topic}",
    backstory = """
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}.
    Known for your ability to find the most relevant information
    and present it in a clear and concise manner.
    Use the SerperDevTool to get the most recent information available.""",
    llm = llm,
    verbose = True,
    tools=[
        SafeSerperDevTool(
            n_results=20
        )
    ]
)


reporting_analyst = SafeAgent(
    role = "Reporting Analyst",
    goal = "Create detailed reports based on {topic} data analysis and research findings",
    backstory = """
    You're a meticulous analyst with a keen eye for detail.
    You're known for your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.""",
    llm = llm,
    verbose = True
)