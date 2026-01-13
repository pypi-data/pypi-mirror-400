from __future__ import annotations
from typing import Optional, List, Union
from pydantic import BaseModel


# ======================================================
# BASE MODEL (allows unknown attributes)
# ======================================================


class XModel(BaseModel):
    model_config = dict(extra="allow")


# ======================================================
# BASIC DATE/TIME
# ======================================================


class PIDateTime(XModel):
    date: str
    time: str


# ======================================================
# PROPERTIES
# ======================================================


class PIStringProperty(XModel):
    key: str
    value: str


class PIDoubleProperty(XModel):
    key: str
    value: float


class PILongProperty(XModel):
    key: str
    value: int


class PIIntProperty(XModel):
    key: str
    value: int


class PIBooleanProperty(XModel):
    key: str
    value: bool


class PIDateProperty(XModel):
    key: str
    date: str


class PIDateTimeProperty(XModel):
    key: str
    date: str
    time: str


PIProperty = Union[
    PIStringProperty,
    PIDoubleProperty,
    PILongProperty,
    PIIntProperty,
    PIBooleanProperty,
    PIDateProperty,
    PIDateTimeProperty,
]


# ======================================================
# THRESHOLDS
# ======================================================


class PIThresholdBase(XModel):
    id: Optional[str] = None
    name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    value: float


class PIHighLevelThreshold(PIThresholdBase):
    pass


class PILowLevelThreshold(PIThresholdBase):
    pass


class PIThresholds(XModel):
    highLevelThreshold: Optional[List[PIHighLevelThreshold]] = None
    lowLevelThreshold: Optional[List[PILowLevelThreshold]] = None


# ======================================================
# TIMESTEP
# ======================================================


class PITimeStep(XModel):
    unit: Optional[str] = None
    multiplier: Optional[int] = None
    minutes: Optional[int] = None


# ======================================================
# EVENT
# ======================================================


class PIEvent(XModel):
    date: Optional[str] = None
    time: Optional[str] = None

    startDate: Optional[str] = None
    startTime: Optional[str] = None
    endDate: Optional[str] = None
    endTime: Optional[str] = None

    value: Optional[Union[float, str]] = None
    minValue: Optional[float] = None
    maxValue: Optional[float] = None

    flag: Optional[int] = None

    # unknown fs:* attributes accepted automatically (via extra="allow")


# ======================================================
# HEADER
# ======================================================


class PIHeader(XModel):
    type: str

    moduleInstanceId: Optional[str] = None
    locationId: str
    parameterId: str

    qualifierId: Optional[List[str]] = None

    ensembleId: Optional[str] = None
    ensembleMemberIndex: Optional[int] = None

    timeStep: Optional[PITimeStep] = None

    startDate: PIDateTime
    endDate: PIDateTime
    forecastDate: Optional[PIDateTime] = None

    missVal: Optional[str] = None
    stationName: Optional[str] = None

    lat: Optional[float] = None
    lon: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

    longName: Optional[str] = None
    units: Optional[str] = None

    sourceOrganisation: Optional[str] = None
    sourceSystem: Optional[str] = None

    fileDescription: Optional[str] = None

    creationDate: Optional[str] = None
    creationTime: Optional[str] = None

    thresholds: Optional[PIThresholds] = None


# ======================================================
# SERIES
# ======================================================


class PISeries(XModel):
    header: PIHeader
    properties: Optional[List[PIProperty]] = None
    event: List[PIEvent]


# ======================================================
# ROOT
# ======================================================


class PITimeSeries(XModel):
    version: Optional[str]
    timeZone: float
    series: List[PISeries]
