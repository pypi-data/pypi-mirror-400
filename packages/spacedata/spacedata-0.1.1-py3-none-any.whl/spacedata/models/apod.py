import datetime

from pydantic import BaseModel, model_validator


class ApodInputParams(BaseModel):
    date: datetime.date | None = None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    count: int | None = None
    thumbs: bool | None = None

    @model_validator(mode="before")
    def validate_dates(cls, values):
        # should be date, or date range
        date, start_date, end_date = (
            values.get("date"),
            values.get("start_date"),
            values.get("end_date"),
        )
        if date and (start_date or end_date):
            raise ValueError("date and start_date/end_date are mutually exclusive")
        if start_date and end_date:
            if start_date > end_date:
                raise ValueError("start_date must be before end_date")
        return values

    @property
    def is_date_range(self) -> bool:
        return self.start_date is not None and self.end_date is not None


class ApodResultItem(BaseModel):
    copyright: str | None = None
    date: datetime.date
    explanation: str
    hdurl: str | None = None
    media_type: str
    service_version: str
    title: str
    url: str
