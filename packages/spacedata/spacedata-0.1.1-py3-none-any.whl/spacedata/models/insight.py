import datetime
import typing

from pydantic import BaseModel, ConfigDict, Field, RootModel


class InSightInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ver: str = Field(default="1.0")
    feedtype: str = Field(default="json")


class InSightSensorData(BaseModel):
    av: float | None = None
    ct: int | None = None
    mn: float | None = None
    mx: float | None = None
    sol_hours_with_data: list[int] | None = None
    valid: bool | None = None


class InSightWindDirectionData(BaseModel):
    compass_degrees: float | None = None
    compass_point: str | None = None
    compass_right: float | None = None
    compass_up: float | None = None
    ct: int | None = None
    sol_hours_with_data: list[int] | None = None
    valid: bool | None = None


class InSightSolData(BaseModel):
    at: InSightSensorData | None = Field(default=None, alias="AT")
    hws: InSightSensorData | None = Field(default=None, alias="HWS")
    pre: InSightSensorData | None = Field(default=None, alias="PRE")
    wd: dict[str, InSightWindDirectionData] | None = Field(default=None, alias="WD")
    first_utc: datetime.datetime | None = Field(default=None, alias="First_UTC")
    last_utc: datetime.datetime | None = Field(default=None, alias="Last_UTC")
    month_ordinal: int | None = Field(default=None, alias="Month_ordinal")
    northern_season: str | None = Field(default=None, alias="Northern_season")
    southern_season: str | None = Field(default=None, alias="Southern_season")
    season: str | None = Field(default=None, alias="Season")


class InSightValidityChecks(BaseModel):
    sol_hours_required: int | None = None
    sols_checked: list[str] | None = None
    model_config = ConfigDict(extra="allow")


class InSightWeatherResult(RootModel):
    root: dict[str, typing.Any]

    def get_sol(self, sol_id: str) -> InSightSolData | None:
        val = self.root.get(sol_id)
        if isinstance(val, dict):
            return InSightSolData.model_validate(val)
        return None

    @property
    def sol_keys(self) -> list[str]:
        val = self.root.get("sol_keys")
        if isinstance(val, list):
            return val
        return []

    @property
    def validity_checks(self) -> InSightValidityChecks | None:
        val = self.root.get("validity_checks")
        if isinstance(val, dict):
            return InSightValidityChecks.model_validate(val)
        return None
