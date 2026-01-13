import typing

if typing.TYPE_CHECKING:
    from spacedata.client import SpaceDataClient


class BaseResource:
    def __init__(self, client: "SpaceDataClient"):
        self.client = client
