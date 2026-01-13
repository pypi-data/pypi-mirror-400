from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from .models import PITimeSeries, PISeries, PIHeader, PIEvent, PIProperty, PIDateTime


def create_pi_header(
    type: str,
    location_id: str,
    parameter_id: str,
    start_date: datetime,
    end_date: datetime,
    **kwargs: Any
) -> PIHeader:
    """
    Creates a PIHeader object.

    Args:
        type (str): The series type (e.g., "instantaneous").
        location_id (str): The ID of the location.
        parameter_id (str): The ID of the parameter.
        start_date (datetime): The start date and time of the series.
        end_date (datetime): The end date and time of the series.
        **kwargs: Additional optional header fields.

    Returns:
        PIHeader: A new PIHeader object.
    """
    header_data = {
        "type": type,
        "locationId": location_id,
        "parameterId": parameter_id,
        "startDate": PIDateTime(
            date=start_date.strftime("%Y-%m-%d"), time=start_date.strftime("%H:%M:%S")
        ),
        "endDate": PIDateTime(
            date=end_date.strftime("%Y-%m-%d"), time=end_date.strftime("%H:%M:%S")
        ),
    }

    if "forecast_date" in kwargs:
        fd = kwargs.pop("forecast_date")
        header_data["forecastDate"] = PIDateTime(
            date=fd.strftime("%Y-%m-%d"), time=fd.strftime("%H:%M:%S")
        )

    header_data.update(kwargs)
    return PIHeader(**header_data)


def create_pi_series(
    header: PIHeader,
    events: List[Dict[str, Any]],
    properties: Optional[List[PIProperty]] = None,
) -> PISeries:
    """
    Creates a PISeries object from a header and event data.

    Args:
        header (PIHeader): The header for the series.
        events (List[Dict[str, Any]]): A list of dictionaries, where each
            dictionary represents an event (e.g., {"date": dt, "value": 1.23}).
        properties (Optional[List[PIProperty]]): An optional list of properties.

    Returns:
        PISeries: A new PISeries object.
    """
    event_objects = []
    for event_data in events:
        if "date" in event_data and isinstance(event_data["date"], datetime):
            dt = event_data.pop("date")
            event_data["date"] = dt.strftime("%Y-%m-%d")
            event_data["time"] = dt.strftime("%H:%M:%S")
        event_objects.append(PIEvent(**event_data))

    return PISeries(header=header, event=event_objects, properties=properties)


def create_pi_timeseries(
    series: Union[PISeries, List[PISeries]],
    time_zone: float = 0.0,
    version: str = "1.25",
) -> PITimeSeries:
    """
    Creates the root PITimeSeries object.

    Args:
        series (Union[PISeries, List[PISeries]]): A single PISeries object or a list of them.
        time_zone (float): The time zone offset. Defaults to 0.0.
        version (str): The PI-XML version. Defaults to "1.25".

    Returns:
        PITimeSeries: The complete PITimeSeries object, ready for writing.
    """
    if not isinstance(series, list):
        series = [series]
    return PITimeSeries(version=version, timeZone=time_zone, series=series)
