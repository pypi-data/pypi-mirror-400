import datetime

from pydantic import BaseModel, Field, field_validator


class NeoFeedInputParams(BaseModel):
    start_date: datetime.date
    end_date: datetime.date


class NeoLookupInputParams(BaseModel):
    asteroid_ids: list[int]

    @field_validator("asteroid_ids", mode="before")
    def validate_asteroid_ids(cls, v):
        if isinstance(v, list):
            return v
        return [v]


class NeoBrowseInputParams(BaseModel):
    size: int = Field(default=20, ge=1, le=20, description="Number of items per page")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(description="How many items to return in total")


class NeoEstimatedDiameterValues(BaseModel):
    min: float = Field(..., validation_alias="estimated_diameter_min")
    max: float = Field(..., validation_alias="estimated_diameter_max")


class NeoEstimatedDiameter(BaseModel):
    kilometers: NeoEstimatedDiameterValues
    meters: NeoEstimatedDiameterValues
    miles: NeoEstimatedDiameterValues
    feet: NeoEstimatedDiameterValues


class NeoRelativeVelocity(BaseModel):
    kilometers_per_second: float
    kilometers_per_hour: float
    miles_per_hour: float


class NeoMissDistance(BaseModel):
    astronomical: float
    lunar: float
    kilometers: float
    miles: float


class NeoCloseApproachData(BaseModel):
    close_approach_date: datetime.date
    epoch_date_close_approach: int
    relative_velocity: NeoRelativeVelocity
    miss_distance: NeoMissDistance
    orbiting_body: str


class NeoOrbitClass(BaseModel):
    orbit_class_type: str
    orbit_class_description: str
    orbit_class_range: str


class NeoOrbitalData(BaseModel):
    orbit_id: int
    orbit_determination_date: datetime.datetime
    first_observation_date: datetime.date
    last_observation_date: datetime.date
    data_arc_in_days: int
    observations_used: int
    orbit_uncertainty: int
    minimum_orbit_intersection: float
    jupiter_tisserand_invariant: float
    epoch_osculation: float
    eccentricity: float
    semi_major_axis: float
    inclination: float
    ascending_node_longitude: float
    orbital_period: float
    perihelion_distance: float
    perihelion_argument: float
    aphelion_distance: float
    perihelion_time: float
    mean_anomaly: float
    mean_motion: float
    equinox: str
    orbit_class: NeoOrbitClass


class NeoItem(BaseModel):
    id: str
    name: str
    neo_reference_id: str
    nasa_jpl_url: str
    absolute_magnitude_h: float
    estimated_diameter: NeoEstimatedDiameter
    is_potentially_hazardous_asteroid: bool
    close_approach_data: list[NeoCloseApproachData]
    is_sentry_object: bool


class NeoFeedResultItem(NeoItem):
    date: datetime.date


class NeoLookupResultItem(NeoItem):
    orbital_data: NeoOrbitalData
