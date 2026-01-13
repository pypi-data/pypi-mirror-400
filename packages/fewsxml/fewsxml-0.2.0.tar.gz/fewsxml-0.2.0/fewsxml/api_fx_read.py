import xml.etree.ElementTree as ET
from .models import (
    PITimeSeries,
    PISeries,
    PIHeader,
    PIEvent,
    PIProperty,
    PIDateTime,
    PIThresholds,
    PIHighLevelThreshold,
    PILowLevelThreshold,
    PIStringProperty,
    PIDoubleProperty,
    PILongProperty,
    PIIntProperty,
    PIBooleanProperty,
    PIDateProperty,
    PIDateTimeProperty,
)


NS = {"pi": "http://www.wldelft.nl/fews/PI"}


# ----------------------------------------------------------------------
# Helper: read date/time composite element
# ----------------------------------------------------------------------
def _parse_date_time(elem: ET.Element) -> PIDateTime:
    return PIDateTime(date=elem.attrib.get("date"), time=elem.attrib.get("time"))


# ----------------------------------------------------------------------
# Helper: parse typed <properties>
# ----------------------------------------------------------------------
def _parse_property(elem: ET.Element) -> PIProperty:

    tag = elem.tag

    # Simple key/value types
    if tag == "string":
        return PIStringProperty(key=elem.attrib["key"], value=elem.attrib["value"])
    if tag == "double":
        return PIDoubleProperty(
            key=elem.attrib["key"], value=float(elem.attrib["value"])
        )
    if tag == "long":
        return PILongProperty(key=elem.attrib["key"], value=int(elem.attrib["value"]))
    if tag == "int":
        return PIIntProperty(key=elem.attrib["key"], value=int(elem.attrib["value"]))
    if tag == "boolean":
        v = elem.attrib["value"].lower() == "true"
        return PIBooleanProperty(key=elem.attrib["key"], value=v)

    # Date property
    if tag == "date":
        return PIDateProperty(key=elem.attrib["key"], date=elem.attrib["value"])

    # Date-time property
    if tag == "dateTime":
        return PIDateTimeProperty(
            key=elem.attrib["key"], date=elem.attrib["date"], time=elem.attrib["time"]
        )

    raise ValueError(f"Unknown property tag: {tag}")


# ----------------------------------------------------------------------
# Helper: thresholds
# ----------------------------------------------------------------------
def _parse_thresholds(elem: ET.Element) -> PIThresholds:
    highs = []
    lows = []

    for h in elem.findall("pi:highLevelThreshold", namespaces=NS):
        attrs = {k: v for k, v in h.attrib.items() if k != "value"}
        highs.append(PIHighLevelThreshold(value=float(h.attrib["value"]), **attrs))

    for lowLevelElem in elem.findall("pi:lowLevelThreshold", namespaces=NS):
        attrs = {k: v for k, v in lowLevelElem.attrib.items() if k != "value"}
        lows.append(
            PILowLevelThreshold(value=float(lowLevelElem.attrib["value"]), **attrs)
        )

    return PIThresholds(
        highLevelThreshold=highs or None, lowLevelThreshold=lows or None
    )


# ----------------------------------------------------------------------
# Helper: parse <event>
# ----------------------------------------------------------------------
def _parse_event(elem: ET.Element) -> PIEvent:
    attrs = dict(elem.attrib)

    # Convert numeric fields where needed
    if "value" in attrs:
        v = attrs["value"]
        try:
            attrs["value"] = float(v)
        except ValueError:
            attrs["value"] = v  # allow NaN or text

    if "minValue" in attrs:
        attrs["minValue"] = float(attrs["minValue"])
    if "maxValue" in attrs:
        attrs["maxValue"] = float(attrs["maxValue"])
    if "flag" in attrs:
        attrs["flag"] = int(attrs["flag"])

    return PIEvent(**attrs)


# ----------------------------------------------------------------------
# Helper: parse <header>
# ----------------------------------------------------------------------
def _parse_header(elem: ET.Element) -> PIHeader:
    type_text = elem.findtext("pi:type", namespaces=NS)
    attribs = {"type": type_text}

    # Required simple text elements:
    locationId = elem.findtext("pi:locationId", namespaces=NS)
    parameterId = elem.findtext("pi:parameterId", namespaces=NS)

    attribs["locationId"] = locationId
    attribs["parameterId"] = parameterId

    # qualifierId list
    qualifiers = [q.text for q in elem.findall("pi:qualifierId", namespaces=NS)]
    if qualifiers:
        attribs["qualifierId"] = qualifiers

    # moduleInstanceId
    if (mi := elem.findtext("pi:moduleInstanceId", namespaces=NS)) is not None:
        attribs["moduleInstanceId"] = mi

    # times
    attribs["startDate"] = _parse_date_time(elem.find("pi:startDate", namespaces=NS))
    attribs["endDate"] = _parse_date_time(elem.find("pi:endDate", namespaces=NS))

    if (fd := elem.find("pi:forecastDate", namespaces=NS)) is not None:
        attribs["forecastDate"] = _parse_date_time(fd)

    # timeStep
    if (ts := elem.find("pi:timeStep", namespaces=NS)) is not None:
        ts_kwargs = {
            k: int(v) if k in ("multiplier", "minutes") else v
            for k, v in ts.attrib.items()
        }
        attribs["timeStep"] = ts_kwargs

    # optional scalar tags
    optional_tags = [
        "missVal",
        "stationName",
        "longName",
        "units",
        "sourceOrganisation",
        "sourceSystem",
        "fileDescription",
        "creationDate",
        "creationTime",
        "lat",
        "lon",
        "x",
        "y",
        "z",
    ]

    for tag in optional_tags:
        if elem.find("pi:" + tag, namespaces=NS) is not None:
            txt = elem.findtext("pi:" + tag, namespaces=NS)
            # float conversion for coords
            if tag in ("lat", "lon", "x", "y", "z"):
                attribs[tag] = float(txt)
            else:
                attribs[tag] = txt

    # thresholds
    if (th := elem.find("pi:thresholds", namespaces=NS)) is not None:
        attribs["thresholds"] = _parse_thresholds(th)

    return PIHeader(**attribs)


# ----------------------------------------------------------------------
# Helper: parse <series>
# ----------------------------------------------------------------------
def _parse_series(elem: ET.Element) -> PISeries:
    header = elem.find("pi:header", NS)
    parsed_header = _parse_header(header)

    # properties
    props_container = elem.find("pi:properties", NS)
    props = None
    if props_container is not None:
        props = [_parse_property(p) for p in list(props_container)]

    # events
    events = [_parse_event(e) for e in elem.findall("pi:event", NS)]

    return PISeries(header=parsed_header, properties=props, event=events)


# ----------------------------------------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------------------------------------


def read(filepath: str) -> PITimeSeries:
    tree = ET.parse(filepath)
    root = tree.getroot()

    version = root.attrib.get("version")

    tz_elem = root.find("pi:timeZone", NS)
    if tz_elem is None or tz_elem.text is None:
        raise ValueError("Missing <timeZone> element")
    timeZone = float(tz_elem.text)

    series = [_parse_series(s) for s in root.findall("pi:series", NS)]

    return PITimeSeries(version=version, timeZone=timeZone, series=series)
