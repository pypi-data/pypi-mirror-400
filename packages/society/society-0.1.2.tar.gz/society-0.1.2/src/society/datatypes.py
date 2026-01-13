import enum
import typing as T
import uuid

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# Simulation Mode
# -----------------------------------------------------------------------------


class SimulationMode(str, enum.Enum):
    """Type of simulation to run"""

    TASK = "task"
    """Team collaborates to solve a task from the CEO"""

    CASUAL = "casual"
    """People casually chat and get to know each other"""


# -----------------------------------------------------------------------------
# Records with UUIDs
# -----------------------------------------------------------------------------


class Person(BaseModel):
    id: uuid.UUID
    name: str
    bio: str
    role: T.Literal["ceo", "member"] = "member"


class Message(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    person: str
    t: float
    channel_id: uuid.UUID
    channel: str
    text: str


class Answer(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    text: str


class Vote(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    answer_id: uuid.UUID
    vote: T.Literal["yes", "no", "unsure"]


class Channel(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    person_ids: list[uuid.UUID]


# -----------------------------------------------------------------------------
# State for execution of the simulation
# -----------------------------------------------------------------------------


class SharedState:
    """
    Shared mutable state in the deps of all agents
    """

    def __init__(self) -> None:
        self.answers: list[Answer] = []
        self.votes: list[Vote] = []
        self.final_answer: Answer | None = None


# -----------------------------------------------------------------------------
# Events emitted by agent runner
# -----------------------------------------------------------------------------


class AgentEvent(BaseModel):
    """
    Event from agent streaming, serializable for IPC
    """

    model_config = {"arbitrary_types_allowed": True}

    kind: str
    person_name: str
    time_s: float
    data: T.Any = None


# -----------------------------------------------------------------------------
# Character generation
# -----------------------------------------------------------------------------


class CharacterOutput(BaseModel):
    uuid: uuid.UUID
    name: str
    birth_year: int | None
    gender: str
    location: str
    occupation: str
    bio: str
    personality: str
    context: str
    emoji: str
    confidence: int

    def format(self) -> str:
        lines: list[str] = [
            "-" * 60,
            f"{self.emoji} {self.name}",
            "-" * 60,
            f"Birth Year: {self.birth_year}",
            f"Gender: {self.gender}",
            f"Location: {self.location}",
            f"Occupation: {self.occupation}",
            f"Bio: {self.bio}",
            f"Personality: {self.personality}",
            f"Context: {self.context}",
        ]
        return "\n".join(lines)
