from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EdgeType(str, Enum):
    co_occurrence = "co-occurrence"


class Edge(BaseModel):
    node_id_1: int
    node_id_2: int
    weight: float
    typ: EdgeType


class NodeType(str, Enum):
    hashtag = "hashtag"
    twitter_user = "twitter user"


class Node(BaseModel):
    id: int
    name: str
    weight: float
    typ: NodeType


class TrendDescription(BaseModel):
    keywords: list[str]
    weights: list[float]


class Network(BaseModel):
    nodes: list[Node]
    edges: list[Edge]
    trend_score: float


class TimeWindow(BaseModel):
    start: datetime
    stop: datetime
