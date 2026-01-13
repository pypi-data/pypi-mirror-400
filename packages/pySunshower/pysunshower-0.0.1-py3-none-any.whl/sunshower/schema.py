"""sunshower/schema.py"""

# Standard library imports.
from enum import Enum
from typing import List

# Third party imports.
from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Any, List


class Model(BaseModel):
    provider: str
    name: str
    prompt: str


class Harness(BaseModel):
    tool_names: List[str] = Field(default=[], alias="tools")
    tools: List[Any] = []

    def model_post_init(self, context: Any) -> None:
        self.tools = []
        for tool_name in self.tool_names:
            match tool_name:
                case "serper":
                    from langchain_community.utilities import GoogleSerperAPIWrapper

                    search = GoogleSerperAPIWrapper()
                    serper_tool = tool(name_or_callable="serper")(search.run)
                    self.tools.append(serper_tool)
                case "whois":
                    from whois import whois

                    whois_tool = tool(name_or_callable="whois")(whois)
                    self.tools.append(whois_tool)
                case _:
                    raise RuntimeError(f"unknown tool: {tool}")


class AgentProfile(BaseModel):
    name: str
    model: Model
    harness: Harness


class TeamProfile(BaseModel):
    name: str
    agent_profiles: List[AgentProfile] = Field(alias="agents")


class MetricType(str, Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    COST = "cost"
    PRECISION = "precision"
    PREFERENCES = "preferences"
    RECALL = "recall"
    SPEED = "speed"
    TRAJECTORY = "trajectory"


class Metric(BaseModel):
    type: MetricType = Field(alias="metric")
    prompt: str


class JudgeProfile(AgentProfile):
    metricsToEvaluate: List[Metric]
    teamsToEvaluate: List[str]


class Spec(BaseModel):
    task: str
    trials: int
    team_profiles: List[TeamProfile] = Field(alias="teams")
    judge_profiles: List[JudgeProfile] = Field(alias="judges")


class Metadata(BaseModel):
    name: str
    description: str


class ExperimentSet(BaseModel):
    apiVersion: str = Field(..., pattern="^v1$")
    kind: str = Field(..., pattern="^ExperimentSet$")
    metadata: Metadata
    spec: Spec
