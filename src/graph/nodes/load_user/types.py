from src.types.nodes import NodeResponse
from src.types.user import User


class LoadUserResponse(NodeResponse):
    user: User
