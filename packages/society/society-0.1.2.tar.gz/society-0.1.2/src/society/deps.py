import datetime
import uuid

from pydantic import BaseModel

from society.chat_client import ChatClient
from society.datatypes import CharacterOutput, SharedState, SimulationMode


class Deps(BaseModel):
    """
    Dependencies passed to each agent
    """

    model_config = {"arbitrary_types_allowed": True}

    character: CharacterOutput
    """ The character this agent is playing """

    chat_client: ChatClient
    """ Per-agent chat client """

    start_timestamp: datetime.datetime
    """ The timestamp when the simulation started """

    simulation_mode: SimulationMode
    """ The type of simulation being run """

    voting_start_s: float = 120.0
    """ The minimum time to start proposing answers and voting (task mode only) """

    shared_state: SharedState
    """ Shared mutable state across all agents """

    @property
    def character_id(self) -> uuid.UUID:
        return self.character.uuid

    def current_time_s(self) -> float:
        delta = datetime.datetime.now() - self.start_timestamp
        return round(delta.total_seconds(), 1)
