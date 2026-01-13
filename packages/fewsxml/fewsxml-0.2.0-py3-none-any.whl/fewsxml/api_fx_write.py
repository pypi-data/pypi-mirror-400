import xml.etree.ElementTree as ET
from xml.dom import minidom
from .models import PITimeSeries


def _set_if_not_none(elem: ET.Element, tag: str, value):
    """Create a subelement <tag>value</tag> if value is not None."""
    if value is not None:
        sub = ET.SubElement(elem, tag)
        sub.text = str(value)


def _add_date_time(parent: ET.Element, tag: str, dt):
    """Create something like: <startDate date="YYYY-MM-DD" time="HH:MM:SS" />"""
    if dt:
        elem = ET.SubElement(parent, tag)
        elem.set("date", dt.date)
        elem.set("time", dt.time)


def _add_time_step(parent: ET.Element, ts):
    if ts:
        elem = ET.SubElement(parent, "timeStep")
        if ts.unit is not None:
            elem.set("unit", ts.unit)
        if ts.multiplier is not None:
            elem.set("multiplier", str(ts.multiplier))
        if ts.minutes is not None:
            elem.set("minutes", str(ts.minutes))


def _add_properties(parent: ET.Element, properties):
    if not properties:
        return
    for p in properties:
        tag = "property"
        # Each property becomes:
        # <property key="..." value="...">
        elem = ET.SubElement(parent, tag)
        elem.set("key", p.key)

        # Identify type-specific fields
        if hasattr(p, "value"):
            elem.set("value", str(p.value))
        if hasattr(p, "date"):
            elem.set("date", p.date)
        if hasattr(p, "time"):
            elem.set("time", p.time)


def _add_thresholds(parent: ET.Element, thresholds):
    if not thresholds:
        return

    ts_elem = ET.SubElement(parent, "thresholds")

    def add(th_list, tag):
        if not th_list:
            return
        for th in th_list:
            elem = ET.SubElement(ts_elem, tag)
            for attr in [
                "id",
                "name",
                "label",
                "description",
                "comment",
                "groupId",
                "groupName",
                "value",
            ]:
                val = getattr(th, attr, None)
                if val is not None:
                    elem.set(attr, str(val))

    add(thresholds.highLevelThreshold, "highLevelThreshold")
    add(thresholds.lowLevelThreshold, "lowLevelThreshold")


def _add_event(parent: ET.Element, ev):
    elem = ET.SubElement(parent, "event")

    # date/time
    if ev.date is not None:
        elem.set("date", ev.date)
    if ev.time is not None:
        elem.set("time", ev.time)

    # start / end date + time
    if ev.startDate is not None:
        elem.set("startDate", ev.startDate)
    if ev.startTime is not None:
        elem.set("startTime", ev.startTime)
    if ev.endDate is not None:
        elem.set("endDate", ev.endDate)
    if ev.endTime is not None:
        elem.set("endTime", ev.endTime)

    # value
    if ev.value is not None:
        elem.set("value", str(ev.value))

    # min/max
    if ev.minValue is not None:
        elem.set("minValue", str(ev.minValue))
    if ev.maxValue is not None:
        elem.set("maxValue", str(ev.maxValue))

    # flag
    if ev.flag is not None:
        elem.set("flag", str(ev.flag))

    # unknown attributes (fs:*)
    for k, v in ev.__dict__.items():
        if k.startswith("fs:"):
            elem.set(k, str(v))


# ---------------------------------------------------------------------
def write(pi: "PITimeSeries", filename: str):
    NS = "http://www.wldelft.nl/fews/PI"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"

    ET.register_namespace("", NS)
    ET.register_namespace("xsi", XSI)

    root = ET.Element(
        f"{{{NS}}}TimeSeries",
        {
            "version": pi.version if pi.version else "",
            f"{{{XSI}}}schemaLocation": f"{NS} https://fewsdocs.deltares.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd",
        },
    )

    # <timeZone>
    _set_if_not_none(root, "timeZone", pi.timeZone)

    # Each <series>
    for s in pi.series:
        s_elem = ET.SubElement(root, "series")

        # ------------------- HEADER -------------------
        h = s.header
        h_elem = ET.SubElement(s_elem, "header")

        _set_if_not_none(h_elem, "type", h.type)
        _set_if_not_none(h_elem, "moduleInstanceId", h.moduleInstanceId)
        _set_if_not_none(h_elem, "locationId", h.locationId)
        _set_if_not_none(h_elem, "parameterId", h.parameterId)

        # qualifierId is a list
        if h.qualifierId:
            for q in h.qualifierId:
                _set_if_not_none(h_elem, "qualifierId", q)

        _set_if_not_none(h_elem, "ensembleId", h.ensembleId)
        _set_if_not_none(h_elem, "ensembleMemberIndex", h.ensembleMemberIndex)

        # timeStep
        _add_time_step(h_elem, h.timeStep)

        # Dates
        _add_date_time(h_elem, "startDate", h.startDate)
        _add_date_time(h_elem, "endDate", h.endDate)
        if h.forecastDate:
            _add_date_time(h_elem, "forecastDate", h.forecastDate)

        # Simple fields
        for tag in [
            "missVal",
            "stationName",
            "lat",
            "lon",
            "x",
            "y",
            "z",
            "longName",
            "units",
            "sourceOrganisation",
            "sourceSystem",
            "fileDescription",
            "creationDate",
            "creationTime",
        ]:
            _set_if_not_none(h_elem, tag, getattr(h, tag))

        # thresholds
        _add_thresholds(h_elem, h.thresholds)

        # ------------------- PROPERTIES -------------------
        _add_properties(s_elem, s.properties)

        # ------------------- EVENTS -------------------
        for ev in s.event:
            _add_event(s_elem, ev)

    # Pretty printing
    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")

    with open(filename, "wb") as f:
        f.write(pretty)
