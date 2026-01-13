from spacedata.resources.base import BaseResource
from spacedata.resources.planetary.apod import apod


class PlanetaryResource(BaseResource):
    apod = apod


__all__ = ["PlanetaryResource"]
