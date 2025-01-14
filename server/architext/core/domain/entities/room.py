from typing import List, Optional
from dataclasses import dataclass, field
from architext.core.domain.entities.exit import Exit

@dataclass
class Room:
    id: str
    name: str
    world_id: str
    description: str = field(default="")
    exits: List[Exit] = field(default_factory=list)

    def get_exit_destination_id(self, exit_name: str) -> Optional[str]:
        return next((e.destination_room_id for e in self.exits if e.name == exit_name), None)
    

DEFAULT_ROOM = Room(
    id="DEFAULT_ROOM",
    name="Initial room",
    description="This is the initial room.",
    exits=[],
    world_id="DEFAULT_WORLD"
)