"""
Automated Test Suite for Serializers, Exporters, and Data Validation
Validates Markdown TOC, CSV/JSON converters, RFC 5545 iCalendar,
RFC 2426 vCard, GPX/KML, OPML 2.0, field validation, and data sanitization.
"""

import json
from backend.core.export_engine import (
    MarkdownExporter,
    TabularExporter,
    CalendarICalExporter,
    VCardExporter,
    GeoSpatialExporter,
    OPMLExporter
)
from backend.core.validation import (
    FieldValidator,
    DataSchema,
    Sanitizer
)


def test_markdown_and_tabular_exporters():
    md = "# Overview\nSome intro text.\n## Architecture\nSystem design.\n### Storage\n17 databases."
    toc = MarkdownExporter.generate_toc(md)
    assert "- [Overview](#overview)" in toc
    assert "- [Architecture](#architecture)" in toc
    assert "- [Storage](#storage)" in toc

    # Table
    records = [{"name": "Aether", "version": 2.0}, {"name": "Kernel", "version": 6.8}]
    table = MarkdownExporter.dict_list_to_table(records)
    assert "| Name | Version |" in table
    assert "| Aether | 2.0 |" in table

    # Tabular CSV <-> JSON
    csv_str = TabularExporter.records_to_csv(records)
    assert "name,version" in csv_str
    parsed = TabularExporter.csv_to_records(csv_str)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "Aether"
    assert parsed[0]["version"] == 2.0


def test_calendar_ical_exporter():
    events = [
        {
            "id": 1,
            "title": "Strategy Briefing",
            "description": "Quarterly operational alignment",
            "start_time": "2026-10-01 10:00:00",
            "end_time": "2026-10-01 11:30:00",
            "location": "War Room",
            "priority": "High",
            "recurrence": "weekly",
            "remind_minutes_before": 15
        }
    ]

    ics_str = CalendarICalExporter.serialize_events(events)
    assert "BEGIN:VCALENDAR" in ics_str
    assert "SUMMARY:Strategy Briefing" in ics_str
    assert "RRULE:FREQ=WEEKLY" in ics_str
    assert "BEGIN:VALARM" in ics_str
    assert "END:VCALENDAR" in ics_str

    parsed = CalendarICalExporter.parse_ics(ics_str)
    assert len(parsed) == 1
    assert parsed[0]["title"] == "Strategy Briefing"


def test_vcard_exporter():
    contact = {
        "first_name": "Elena",
        "last_name": "Rostova",
        "organization": "Helios Labs",
        "job_title": "Lead Cryptographer",
        "phone_primary": "+1 555 123 4567",
        "email_primary": "elena@helios.local",
        "address": "Zurich, Switzerland",
        "website": "https://helios.local",
        "relationship_category": "VIP",
        "notes": "Verified sovereign key."
    }

    vcard_str = VCardExporter.serialize_vcard(contact)
    assert "BEGIN:VCARD" in vcard_str
    assert "FN:Elena Rostova" in vcard_str
    assert "ORG:Helios Labs" in vcard_str
    assert "END:VCARD" in vcard_str

    parsed = VCardExporter.parse_vcard(vcard_str)
    assert parsed["first_name"] == "Elena"
    assert parsed["last_name"] == "Rostova"
    assert parsed["organization"] == "Helios Labs"


def test_geospatial_and_opml_exporters():
    waypoints = [
        {"name": "Svalbard", "latitude": 78.2358, "longitude": 15.4913, "category": "Vault", "notes": "Seed vault"}
    ]

    # GeoJSON
    geojson_str = GeoSpatialExporter.waypoints_to_geojson(waypoints)
    geo = json.loads(geojson_str)
    assert geo["type"] == "FeatureCollection"
    assert len(geo["features"]) == 1

    # GPX 1.1
    gpx = GeoSpatialExporter.waypoints_to_gpx(waypoints)
    assert "<gpx" in gpx
    assert 'lat="78.2358"' in gpx
    assert "<name>Svalbard</name>" in gpx

    # KML 2.2
    kml = GeoSpatialExporter.waypoints_to_kml(waypoints)
    assert "<kml" in kml
    assert "<Placemark>" in kml

    # OPML 2.0
    feeds = [{"title": "Ars Technica", "feed_url": "https://arstechnica.com/rss", "category": "Tech"}]
    opml = OPMLExporter.export_opml(feeds)
    assert "<opml" in opml
    assert 'xmlUrl="https://arstechnica.com/rss"' in opml


def test_field_validators():
    assert FieldValidator.is_valid_email("operator@aether.local") is True
    assert FieldValidator.is_valid_email("invalid_email") is False

    assert FieldValidator.is_valid_url("https://duckduckgo.com") is True
    assert FieldValidator.is_valid_url("ftp://unsupported") is False

    assert FieldValidator.is_valid_ipv4("192.168.1.1") is True
    assert FieldValidator.is_valid_ipv4("999.1.1.1") is False

    assert FieldValidator.is_valid_hex_color("#6366f1") is True
    assert FieldValidator.is_valid_hex_color("blue") is False

    assert FieldValidator.is_valid_coordinate(40.7128, -74.0060) is True
    assert FieldValidator.is_valid_coordinate(105.0, 0.0) is False


def test_data_schema_and_sanitizers():
    schema = DataSchema({
        "username": {"type": str, "required": True, "min_len": 3, "max_len": 20},
        "port": {"type": int, "required": True, "min_val": 1, "max_val": 65535},
        "active": {"type": bool, "required": False, "default": True}
    })

    # Valid
    valid, cleaned, errors = schema.validate({"username": "alex", "port": 8080})
    assert valid is True
    assert cleaned["active"] is True

    # Invalid
    valid, _, errors = schema.validate({"username": "al", "port": 70000})
    assert valid is False
    assert "username" in errors
    assert "port" in errors

    # Sanitizer
    tracking_url = "https://example.com/article?utm_source=twitter&utm_medium=social&fbclid=IwAR123&keep=valid"
    clean_url = Sanitizer.strip_tracking_params(tracking_url)
    assert "utm_source" not in clean_url
    assert "fbclid" not in clean_url
    assert "keep=valid" in clean_url

    # HTML Sanitizer
    dirty_html = "<p>Clean text<script>alert('xss')</script><a href='javascript:void(0)'>Click</a></p>"
    clean_html = Sanitizer.sanitize_html(dirty_html)
    assert "<script" not in clean_html
    assert "javascript:" not in clean_html
