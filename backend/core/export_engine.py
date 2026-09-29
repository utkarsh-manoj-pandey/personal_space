"""
Aether Core Export & Serialization Engine
Universal multi-format document, calendar, directory, and geospatial serializer:
- Markdown & HTML: Structured text, AST table formatting, TOC generation.
- Tabular Data: High-precision CSV <-> JSON converters with column type inference.
- Calendar Synchronization: RFC 5545 iCalendar (iCal / .ics) generator and parser with RRULE support.
- Contact Directory: RFC 2426 (vCard 3.0) and RFC 6350 (vCard 4.0) generator and parser.
- Geospatial XML: GPX 1.1 tracks/waypoints, KML 2.2 schemas, GeoJSON FeatureCollections.
- News Feeds: OPML 2.0 subscription manager import and export.
"""

import re
import csv
import io
import json
import datetime
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional


# =============================================================================
# 1. MARKDOWN & TABULAR EXPORTERS
# =============================================================================

class MarkdownExporter:
    """
    Structured Markdown document assembler and HTML renderer.
    """

    @staticmethod
    def generate_toc(markdown_text: str) -> str:
        """Extract all Markdown headers and compile an indented Table of Contents."""
        lines = markdown_text.splitlines()
        toc_lines = ["## Table of Contents\n"]
        for line in lines:
            m = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                slug = re.sub(r'[^\w\- ]', '', title).lower().replace(' ', '-')
                indent = "  " * (level - 1)
                toc_lines.append(f"{indent}- [{title}](#{slug})")
        return "\n".join(toc_lines)

    @staticmethod
    def dict_list_to_table(records: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """Converts a list of dictionary records into a formatted Markdown table."""
        if not records:
            return ""

        cols = headers if headers else list(records[0].keys())
        header_row = "| " + " | ".join(str(c).capitalize() for c in cols) + " |"
        sep_row = "| " + " | ".join("---" for _ in cols) + " |"

        rows = [header_row, sep_row]
        for r in records:
            row_cells = [str(r.get(c, "")).replace("|", "\\|").replace("\n", " ") for c in cols]
            rows.append("| " + " | ".join(row_cells) + " |")

        return "\n".join(rows)

    @staticmethod
    def to_clean_html(markdown_text: str) -> str:
        """
        Fast lightweight Markdown to HTML converter.
        Handles headings, bold, italics, code blocks, blockquotes, lists, and line breaks.
        """
        out = []
        in_code_block = False

        for line in markdown_text.splitlines():
            if line.startswith("```"):
                in_code_block = not in_code_block
                out.append("<pre><code>" if in_code_block else "</code></pre>")
                continue

            if in_code_block:
                out.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
                continue

            # Headings
            m_h = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m_h:
                lvl = len(m_h.group(1))
                txt = m_h.group(2)
                out.append(f"<h{lvl}>{txt}</h{lvl}>")
                continue

            # Blockquotes
            if line.startswith("> "):
                out.append(f"<blockquote>{line[2:]}</blockquote>")
                continue

            # Unordered lists
            if line.startswith("- ") or line.startswith("* "):
                out.append(f"<li>{line[2:]}</li>")
                continue

            # Inline styling
            processed = line
            processed = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', processed)
            processed = re.sub(r'\*(.+?)\*', r'<em>\1</em>', processed)
            processed = re.sub(r'`(.+?)`', r'<code>\1</code>', processed)
            processed = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', processed)

            if processed.strip():
                out.append(f"<p>{processed}</p>")

        return "\n".join(out)


class TabularExporter:
    """
    Bidirectional CSV, TSV, and JSON tabular dataset transformation engine.
    """

    @staticmethod
    def records_to_csv(records: List[Dict[str, Any]]) -> str:
        """Converts dictionary records to RFC 4180 CSV string."""
        if not records:
            return ""
        output = io.StringIO()
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
        return output.getvalue()

    @staticmethod
    def csv_to_records(csv_text: str) -> List[Dict[str, Any]]:
        """Parses CSV text and auto-casts numerical and boolean fields."""
        if not csv_text.strip():
            return []
        input_stream = io.StringIO(csv_text.strip())
        reader = csv.DictReader(input_stream)
        records = []

        def _infer_type(val: str) -> Any:
            v = val.strip()
            if v == "":
                return None
            if v.lower() == "true":
                return True
            if v.lower() == "false":
                return False
            try:
                if "." in v:
                    return float(v)
                return int(v)
            except ValueError:
                return v

        for row in reader:
            parsed_row = {k: _infer_type(v) for k, v in row.items()}
            records.append(parsed_row)
        return records


# =============================================================================
# 2. CALENDAR RFC 5545 iCALENDAR EXPORTER
# =============================================================================

class CalendarICalExporter:
    """
    Generates and parses RFC 5545 compliant iCalendar (.ics) files.
    """

    @staticmethod
    def serialize_events(events: List[Dict[str, Any]], prod_id: str = "-//Aether Workstation//Calendar 2.0//EN") -> str:
        """
        Serializes calendar event records into standard iCalendar string.
        """
        now_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:{prod_id}",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]

        for ev in events:
            ev_id = ev.get("id", "0")
            uid = f"aether-cal-{ev_id}-{now_stamp}@workstation.local"
            summary = ev.get("title", "Untitled Event").replace("\n", " ").replace(";", "\\;")
            desc = ev.get("description", "").replace("\n", "\\n").replace(";", "\\;")
            loc = ev.get("location", "").replace("\n", " ")
            priority_val = 1 if ev.get("priority") == "Critical" else (3 if ev.get("priority") == "High" else 5)

            # Format start and end
            start_raw = ev.get("start_time", "")
            end_raw = ev.get("end_time", "")

            def _clean_dt(dt_str: str) -> str:
                clean = re.sub(r'[-: ]', '', dt_str)
                if len(clean) >= 14:
                    return f"{clean[:8]}T{clean[8:14]}"
                elif len(clean) >= 8:
                    return f"{clean[:8]}T000000"
                return now_stamp[:15]

            dt_start = _clean_dt(start_raw)
            dt_end = _clean_dt(end_raw)

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART:{dt_start}",
                f"DTEND:{dt_end}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{desc}",
                f"LOCATION:{loc}",
                f"PRIORITY:{priority_val}",
                f"STATUS:CONFIRMED"
            ])

            # Recurrence RRULE
            recurrence = ev.get("recurrence", "none").lower()
            if recurrence == "daily":
                lines.append("RRULE:FREQ=DAILY")
            elif recurrence == "weekly":
                lines.append("RRULE:FREQ=WEEKLY")
            elif recurrence == "monthly":
                lines.append("RRULE:FREQ=MONTHLY")
            elif recurrence == "yearly":
                lines.append("RRULE:FREQ=YEARLY")

            # Alarm reminder
            remind_mins = ev.get("remind_minutes_before", 0)
            if remind_mins and remind_mins > 0:
                lines.extend([
                    "BEGIN:VALARM",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:Reminder: {summary}",
                    f"TRIGGER:-PT{remind_mins}M",
                    "END:VALARM"
                ])

            lines.append("END:VEVENT")

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

    @staticmethod
    def parse_ics(ics_content: str) -> List[Dict[str, Any]]:
        """
        Parses iCalendar content and extracts event dictionaries.
        """
        events = []
        current_event = None

        for raw_line in ics_content.splitlines():
            line = raw_line.strip()
            if line == "BEGIN:VEVENT":
                current_event = {}
            elif line == "END:VEVENT" and current_event is not None:
                events.append(current_event)
                current_event = None
            elif current_event is not None and ":" in line:
                key_part, val_part = line.split(":", 1)
                key = key_part.split(";")[0].upper()
                val = val_part.replace("\\n", "\n").replace("\\;", ";")

                if key == "SUMMARY":
                    current_event["title"] = val
                elif key == "DESCRIPTION":
                    current_event["description"] = val
                elif key == "LOCATION":
                    current_event["location"] = val
                elif key == "DTSTART":
                    current_event["start_time"] = val
                elif key == "DTEND":
                    current_event["end_time"] = val
                elif key == "RRULE":
                    current_event["rrule"] = val

        return events


# =============================================================================
# 3. CONTACT DIRECTORY RFC 2426 / 6350 vCARD EXPORTER
# =============================================================================

class VCardExporter:
    """
    Encodes and decodes contacts using RFC 2426 (vCard 3.0) standards.
    """

    @staticmethod
    def serialize_vcard(contact: Dict[str, Any]) -> str:
        """Converts contact dictionary into RFC 2426 vCard 3.0 record."""
        fn = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip() or "Anonymous"
        n_last = contact.get('last_name', '')
        n_first = contact.get('first_name', '')
        org = contact.get('organization', '')
        title = contact.get('job_title', '')
        phone1 = contact.get('phone_primary', '')
        phone2 = contact.get('phone_secondary', '')
        email1 = contact.get('email_primary', '')
        email2 = contact.get('email_secondary', '')
        addr = contact.get('address', '')
        url = contact.get('website', '')
        note = contact.get('notes', '')
        bday = contact.get('birthday', '')
        cat = contact.get('relationship_category', 'General')

        now_rev = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{fn}",
            f"N:{n_last};{n_first};;;",
            f"REV:{now_rev}"
        ]

        if org:
            lines.append(f"ORG:{org}")
        if title:
            lines.append(f"TITLE:{title}")
        if phone1:
            lines.append(f"TEL;TYPE=WORK,VOICE:{phone1}")
        if phone2:
            lines.append(f"TEL;TYPE=HOME,VOICE:{phone2}")
        if email1:
            lines.append(f"EMAIL;TYPE=PREF,INTERNET:{email1}")
        if email2:
            lines.append(f"EMAIL;TYPE=INTERNET:{email2}")
        if addr:
            lines.append(f"ADR;TYPE=WORK:;;{addr};;;;")
        if url:
            lines.append(f"URL:{url}")
        if bday:
            lines.append(f"BDAY:{bday}")
        if cat:
            lines.append(f"CATEGORIES:{cat}")
        if note:
            lines.append(f"NOTE:{note.replace(chr(10), ' ')}")

        lines.append("END:VCARD")
        return "\r\n".join(lines) + "\r\n"

    @staticmethod
    def parse_vcard(vcard_text: str) -> Dict[str, Any]:
        """Parses vCard string into clean profile dictionary."""
        profile: Dict[str, Any] = {
            "first_name": "", "last_name": "", "organization": "",
            "job_title": "", "phone_primary": "", "phone_secondary": "",
            "email_primary": "", "email_secondary": "", "address": "",
            "website": "", "relationship_category": "General", "notes": "",
            "birthday": ""
        }

        for raw_line in vcard_text.splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            prop_part, val = line.split(":", 1)
            prop = prop_part.split(";")[0].upper()

            if prop == "N":
                parts = val.split(";")
                if len(parts) >= 2:
                    profile["last_name"] = parts[0].strip()
                    profile["first_name"] = parts[1].strip()
            elif prop == "FN" and not profile["first_name"]:
                names = val.split(" ", 1)
                profile["first_name"] = names[0].strip()
                if len(names) > 1:
                    profile["last_name"] = names[1].strip()
            elif prop == "ORG":
                profile["organization"] = val.strip()
            elif prop == "TITLE":
                profile["job_title"] = val.strip()
            elif prop == "TEL":
                if not profile["phone_primary"]:
                    profile["phone_primary"] = val.strip()
                else:
                    profile["phone_secondary"] = val.strip()
            elif prop == "EMAIL":
                if not profile["email_primary"]:
                    profile["email_primary"] = val.strip()
                else:
                    profile["email_secondary"] = val.strip()
            elif prop == "ADR":
                addr_parts = [p.strip() for p in val.split(";") if p.strip()]
                profile["address"] = ", ".join(addr_parts)
            elif prop == "URL":
                profile["website"] = val.strip()
            elif prop == "NOTE":
                profile["notes"] = val.strip()
            elif prop == "BDAY":
                profile["birthday"] = val.strip()
            elif prop == "CATEGORIES":
                profile["relationship_category"] = val.strip()

        return profile


# =============================================================================
# 4. GEOSPATIAL EXPORTERS: GPX, KML, GEOJSON
# =============================================================================

class GeoSpatialExporter:
    """
    Serializes navigation waypoints and trajectories into open GIS standards.
    """

    @staticmethod
    def waypoints_to_geojson(waypoints: List[Dict[str, Any]]) -> str:
        """Converts waypoints list to GeoJSON FeatureCollection."""
        features = []
        for wp in waypoints:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(wp.get("longitude", 0.0)), float(wp.get("latitude", 0.0))]
                },
                "properties": {
                    "name": wp.get("name", "Waypoint"),
                    "category": wp.get("category", "General"),
                    "notes": wp.get("notes", "")
                }
            })
        collection = {
            "type": "FeatureCollection",
            "features": features
        }
        return json.dumps(collection, indent=2)

    @staticmethod
    def waypoints_to_gpx(waypoints: List[Dict[str, Any]], creator: str = "Aether Navigation") -> str:
        """Converts waypoints list to GPX 1.1 XML format."""
        root = ET.Element("gpx", {
            "version": "1.1",
            "creator": creator,
            "xmlns": "http://www.topografix.com/GPX/1/1"
        })

        for wp in waypoints:
            wpt = ET.SubElement(root, "wpt", {
                "lat": str(wp.get("latitude", 0.0)),
                "lon": str(wp.get("longitude", 0.0))
            })
            name_el = ET.SubElement(wpt, "name")
            name_el.text = wp.get("name", "Waypoint")
            desc_el = ET.SubElement(wpt, "desc")
            desc_el.text = wp.get("notes", "")
            type_el = ET.SubElement(wpt, "type")
            type_el.text = wp.get("category", "Waypoint")

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    @staticmethod
    def waypoints_to_kml(waypoints: List[Dict[str, Any]], doc_name: str = "Aether Waypoints") -> str:
        """Converts waypoints list to Google Earth / GIS KML 2.2 XML."""
        root = ET.Element("kml", {"xmlns": "http://www.opengis.net/kml/2.2"})
        doc = ET.SubElement(root, "Document")
        doc_n = ET.SubElement(doc, "name")
        doc_n.text = doc_name

        for wp in waypoints:
            pm = ET.SubElement(doc, "Placemark")
            p_name = ET.SubElement(pm, "name")
            p_name.text = wp.get("name", "Waypoint")
            p_desc = ET.SubElement(pm, "description")
            p_desc.text = f"{wp.get('category', '')} - {wp.get('notes', '')}"
            pt = ET.SubElement(pm, "Point")
            coords = ET.SubElement(pt, "coordinates")
            coords.text = f"{wp.get('longitude', 0.0)},{wp.get('latitude', 0.0)},0"

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


# =============================================================================
# 5. NEWS FEEDS OPML EXPORTER
# =============================================================================

class OPMLExporter:
    """
    Outline Processor Markup Language (OPML 2.0) import and export for RSS feeds.
    """

    @staticmethod
    def export_opml(feeds: List[Dict[str, Any]], title: str = "Aether Intelligence RSS Feeds") -> str:
        """Export feed records into OPML 2.0 XML."""
        root = ET.Element("opml", {"version": "2.0"})
        head = ET.SubElement(root, "head")
        t_el = ET.SubElement(head, "title")
        t_el.text = title
        dt_el = ET.SubElement(head, "dateCreated")
        dt_el.text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

        body = ET.SubElement(root, "body")

        # Group by category
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for f in feeds:
            cat = f.get("category", "General")
            categories.setdefault(cat, []).append(f)

        for cat, items in categories.items():
            cat_outline = ET.SubElement(body, "outline", {"text": cat, "title": cat})
            for item in items:
                ET.SubElement(cat_outline, "outline", {
                    "type": "rss",
                    "text": item.get("title", "Feed"),
                    "title": item.get("title", "Feed"),
                    "xmlUrl": item.get("feed_url", ""),
                    "htmlUrl": item.get("website_url", "")
                })

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    @staticmethod
    def parse_opml(opml_xml: str) -> List[Dict[str, Any]]:
        """Parses OPML XML into list of feed dictionaries."""
        root = ET.fromstring(opml_xml)
        feeds = []
        for outline in root.findall(".//outline[@xmlUrl]"):
            feeds.append({
                "title": outline.get("title") or outline.get("text") or "Untitled Feed",
                "feed_url": outline.get("xmlUrl", ""),
                "website_url": outline.get("htmlUrl", ""),
                "category": outline.get("category", "General")
            })
        return feeds
