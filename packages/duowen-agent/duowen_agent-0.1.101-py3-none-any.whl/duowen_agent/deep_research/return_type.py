from typing import Literal, Optional, List

from pydantic import BaseModel

from duowen_agent.agents.react import ReactObservation, ReactAction, ReactResult


class MsgInfo(BaseModel):
    content: str


class HumanFeedbackInfo(BaseModel):
    type: Literal["str"] = "str"
    content: str


class PlanStep(BaseModel):
    title: str
    description: Optional[str]
    status: Literal["success", "running", "failed", "waiting"]


class PlanInfo(BaseModel):
    title: str
    steps: List[PlanStep]


class ReactStartInfo(BaseModel):
    content: str
    node_id: str


class ReactObservationInfo(ReactObservation):
    node_id: str


class ReactActionInfo(ReactAction):
    node_id: str


class ReactResultInfo(ReactResult):
    node_id: str


class ReactEndInfo(BaseModel):
    content: str
    node_id: str


class ResultInfo(BaseModel):
    type: Literal["msg", "markdown"]
    file_name: Optional[str] = None
    content: str
