from spacedata.resources.base import BaseResource
from spacedata.resources.insight.weather import mars_weather


class InSightResource(BaseResource):
    mars_weather = mars_weather
