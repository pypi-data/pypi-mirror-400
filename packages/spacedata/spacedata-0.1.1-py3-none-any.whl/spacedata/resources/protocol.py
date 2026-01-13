import typing

if typing.TYPE_CHECKING:
    from spacedata.client import SpaceDataClient


class BaseResourceProtocol(typing.Protocol):
    client: "SpaceDataClient"
