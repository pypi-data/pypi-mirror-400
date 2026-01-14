from enum import Enum


class GetTopologyResponse200BrokersItemPartitionsItemRole(str, Enum):
    FOLLOWER = "follower"
    INACTIVE = "inactive"
    LEADER = "leader"

    def __str__(self) -> str:
        return str(self.value)
