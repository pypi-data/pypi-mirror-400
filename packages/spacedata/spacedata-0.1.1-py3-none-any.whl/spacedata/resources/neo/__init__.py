from spacedata.resources.base import BaseResource
from spacedata.resources.neo.browse import browse
from spacedata.resources.neo.feed import feed
from spacedata.resources.neo.lookup import lookup


class NeoResource(BaseResource):
    browse = browse
    feed = feed
    lookup = lookup


__all__ = ["NeoResource"]
