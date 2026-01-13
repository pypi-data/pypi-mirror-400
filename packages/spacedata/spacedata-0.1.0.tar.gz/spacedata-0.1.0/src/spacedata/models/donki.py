import datetime

from pydantic import BaseModel, ConfigDict, Field


class DONKIDateRangeInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    start_date: datetime.date | None = Field(
        alias="startDate",
        default_factory=lambda: datetime.date.today() - datetime.timedelta(days=30),
    )
    end_date: datetime.date | None = Field(
        alias="endDate", default_factory=lambda: datetime.date.today()
    )


class DONKICmeAnalysisInput(DONKIDateRangeInput):
    most_accurate_only: bool | None = Field(alias="mostAccurateOnly", default=None)
    complete_entry_only: bool | None = Field(alias="completeEntryOnly", default=None)
    speed: float | None = Field(default=None)
    half_angle: float | None = Field(alias="halfAngle", default=None)
    catalog: str | None = Field(default=None)
    keyword: str | None = Field(default=None)


class DONKINotificationInput(DONKIDateRangeInput):
    type: str | None = Field(default=None)


class DONKICmeInstrument(BaseModel):
    display_name: str = Field(validation_alias="displayName")


class DONKICmeImpact(BaseModel):
    is_glancing_blow: bool = Field(..., validation_alias="isGlancingBlow")
    is_minor_impact: bool = Field(..., validation_alias="isMinorImpact")
    location: str
    arrival_time: datetime.datetime = Field(..., validation_alias="arrivalTime")


class DONKICmeEnlil(BaseModel):
    model_completion_time: datetime.datetime = Field(
        ...,
        validation_alias="modelCompletionTime",
    )
    au: float
    estimated_shock_arrival_time: datetime.datetime | None = Field(
        ...,
        validation_alias="estimatedShockArrivalTime",
    )
    estimated_duration: float | None = Field(
        ...,
        validation_alias="estimatedDuration",
    )
    rmin_re: float | None
    kp_18: float | None
    kp_90: float | None
    kp_135: float | None
    kp_180: float | None
    is_earth_gb: bool = Field(..., validation_alias="isEarthGB")
    is_earth_minor_impact: bool = Field(..., validation_alias="isEarthMinorImpact")
    link: str
    impact_list: list[DONKICmeImpact] | None = Field(..., validation_alias="impactList")
    cme_ids: list[str] = Field(..., validation_alias="cmeIDs")


class DONKICmeAnalysis(BaseModel):
    is_most_accurate: bool = Field(..., validation_alias="isMostAccurate")
    time_21_5: datetime.datetime = Field(..., validation_alias="time21_5")
    latitude: float | None
    longitude: float | None
    half_angle: float = Field(..., validation_alias="halfAngle")
    speed: float
    type: str
    feature_code: str = Field(..., validation_alias="featureCode")
    image_type: str | None = Field(..., validation_alias="imageType")
    measurement_technique: str | None = Field(
        ..., validation_alias="measurementTechnique"
    )
    note: str
    level_of_data: int | None = Field(validation_alias="levelOfData", default=None)
    tilt: float | None
    minor_half_width: float | None = Field(..., validation_alias="minorHalfWidth")
    speed_measured_at_height: float | None = Field(
        ..., validation_alias="speedMeasuredAtHeight"
    )
    submission_time: datetime.datetime = Field(..., validation_alias="submissionTime")
    enlil_list: list[DONKICmeEnlil] | None = Field(
        validation_alias="enlilList", default=None
    )
    link: str


class DONKILinkedEvent(BaseModel):
    activity_id: str = Field(..., validation_alias="activityID")


class DONKINotification(BaseModel):
    message_type: str | None = Field(default=None, validation_alias="messageType")
    message_id: str = Field(..., validation_alias="messageID")
    message_url: str = Field(..., validation_alias="messageURL")
    message_issue_time: datetime.datetime = Field(
        ..., validation_alias="messageIssueTime"
    )
    message_body: str | None = Field(default=None, validation_alias="messageBody")


class DONKIBaseModel(BaseModel):
    submission_time: datetime.datetime | None = Field(
        default=None, validation_alias="submissionTime"
    )
    version_id: int = Field(..., validation_alias="versionId")
    link: str | None = Field(default=None)
    linked_events: list[DONKILinkedEvent] | None = Field(
        validation_alias="linkedEvents", default=None
    )
    sent_notifications: list[DONKINotification] | None = Field(
        validation_alias="sentNotifications", default=None
    )


class DONKICme(DONKIBaseModel):
    activity_id: str = Field(..., validation_alias="activityID")
    catalog: str
    start_time: datetime.datetime = Field(..., validation_alias="startTime")
    instruments: list[DONKICmeInstrument]
    source_location: str = Field(..., validation_alias="sourceLocation")
    active_region_num: int | None = Field(..., validation_alias="activeRegionNum")
    note: str
    cme_analyses: list[DONKICmeAnalysis] = Field(..., validation_alias="cmeAnalyses")


class DONKIGstKpIndex(BaseModel):
    observed_time: datetime.datetime = Field(..., validation_alias="observedTime")
    kp_index: float = Field(..., validation_alias="kpIndex")
    source: str


class DONKIGst(DONKIBaseModel):
    gst_id: str = Field(..., validation_alias="gstID")
    start_time: datetime.datetime = Field(..., validation_alias="startTime")
    all_kp_index: list[DONKIGstKpIndex] | None = Field(
        validation_alias="allKpIndex", default=None
    )


class DONKIIpsInput(DONKIDateRangeInput):
    location: str | None = Field(default=None)
    catalog: str | None = Field(default=None)


class DONKIIps(DONKIBaseModel):
    activity_id: str = Field(..., validation_alias="activityID")
    catalog: str | None = Field(default=None)
    location: str
    event_time: datetime.datetime = Field(..., validation_alias="eventTime")
    instruments: list[DONKICmeInstrument] | None = Field(default=None)


class DONKIFlr(DONKIBaseModel):
    flr_id: str = Field(..., validation_alias="flrID")
    catalog: str
    instruments: list[DONKICmeInstrument]
    begin_time: datetime.datetime = Field(..., validation_alias="beginTime")
    peak_time: datetime.datetime | None = Field(..., validation_alias="peakTime")
    end_time: datetime.datetime | None = Field(..., validation_alias="endTime")
    class_type: str = Field(..., validation_alias="classType")
    source_location: str = Field(..., validation_alias="sourceLocation")
    active_region_num: int | None = Field(..., validation_alias="activeRegionNum")
    note: str


class DONKISep(DONKIBaseModel):
    sep_id: str = Field(..., validation_alias="sepID")
    event_time: datetime.datetime = Field(..., validation_alias="eventTime")
    instruments: list[DONKICmeInstrument]


class DONKIMpc(DONKIBaseModel):
    mpc_id: str = Field(..., validation_alias="mpcID")
    event_time: datetime.datetime = Field(..., validation_alias="eventTime")
    instruments: list[DONKICmeInstrument]


class DONKIRbe(DONKIBaseModel):
    rbe_id: str = Field(..., validation_alias="rbeID")
    event_time: datetime.datetime = Field(..., validation_alias="eventTime")
    instruments: list[DONKICmeInstrument]


class DONKIHss(DONKIBaseModel):
    hss_id: str = Field(..., validation_alias="hssID")
    event_time: datetime.datetime = Field(..., validation_alias="eventTime")
    instruments: list[DONKICmeInstrument]


class DONKIWsaCmeInput(BaseModel):
    cme_start_time: datetime.datetime = Field(..., validation_alias="cmeStartTime")
    latitude: float
    longitude: float
    speed: float
    half_angle: float = Field(..., validation_alias="halfAngle")
    time21_5: datetime.datetime = Field(..., validation_alias="time21_5")
    feature_code: str | None = Field(default=None, validation_alias="featureCode")
    is_most_accurate: bool = Field(..., validation_alias="isMostAccurate")
    level_of_data: int = Field(..., validation_alias="levelOfData")
    ips_list: list[DONKIIps] | None = Field(default=None, validation_alias="ipsList")
    cmeid: str


class DONKIWsa(BaseModel):
    simulation_id: str = Field(..., validation_alias="simulationID")
    model_completion_time: datetime.datetime = Field(
        ..., validation_alias="modelCompletionTime"
    )
    au: float
    cme_inputs: list[DONKIWsaCmeInput] | None = Field(
        default=None, validation_alias="cmeInputs"
    )
    estimated_shock_arrival_time: datetime.datetime | None = Field(
        default=None, validation_alias="estimatedShockArrivalTime"
    )
    estimated_duration: float | None = Field(
        default=None, validation_alias="estimatedDuration"
    )
    rmin_re: float | None = Field(default=None)
    kp_18: float | None = Field(default=None)
    kp_90: float | None = Field(default=None)
    kp_135: float | None = Field(default=None)
    kp_180: float | None = Field(default=None)
    is_earth_gb: bool = Field(..., validation_alias="isEarthGB")
    is_earth_minor_impact: bool = Field(..., validation_alias="isEarthMinorImpact")
    impact_list: list[DONKICmeImpact] | None = Field(
        default=None, validation_alias="impactList"
    )
    link: str
