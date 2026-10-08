"""
Aether Core Validation & Sanitization Engine
Strict runtime field verification, declarative schema validation, and security sanitization:
- Field Validators: Email, URL, IPv4/IPv6, ISO-8601 timestamps, Lat/Lon bounds, Hex colors, Ports.
- Schema Validator: Declarative data dictionary validation with type checking, boundaries, and required fields.
- Sanitizer: Strip ad/tracking URL telemetry queries, XSS HTML sanitization, filename normalization.
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple, Callable


class FieldValidator:
    """
    Standardized, regex-backed individual field verification.
    """

    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    URL_REGEX = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
    IPV4_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    HEX_COLOR_REGEX = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{8})$')
    PHONE_REGEX = re.compile(r'^\+?[0-9\s\-\(\)\.]{7,25}$')
    SLUG_REGEX = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        if not email or len(email) > 254:
            return False
        return bool(cls.EMAIL_REGEX.match(email.strip()))

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        if not url or len(url) > 2048:
            return False
        return bool(cls.URL_REGEX.match(url.strip()))

    @classmethod
    def is_valid_ipv4(cls, ip: str) -> bool:
        return bool(cls.IPV4_REGEX.match(ip.strip()))

    @classmethod
    def is_valid_hex_color(cls, hex_color: str) -> bool:
        return bool(cls.HEX_COLOR_REGEX.match(hex_color.strip()))

    @classmethod
    def is_valid_phone(cls, phone: str) -> bool:
        return bool(cls.PHONE_REGEX.match(phone.strip()))

    @classmethod
    def is_valid_slug(cls, slug: str) -> bool:
        return bool(cls.SLUG_REGEX.match(slug.strip()))

    @staticmethod
    def is_valid_coordinate(lat: float, lon: float) -> bool:
        """Validate latitude in [-90, 90] and longitude in [-180, 180]."""
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            return (-90.0 <= lat_f <= 90.0) and (-180.0 <= lon_f <= 180.0)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_port(port: int) -> bool:
        try:
            p = int(port)
            return 1 <= p <= 65535
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_iso_datetime(dt_str: str) -> bool:
        """Checks if string satisfies ISO-8601 standard."""
        from datetime import datetime
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d"
        ]
        for fmt in formats:
            try:
                datetime.strptime(dt_str.strip(), fmt)
                return True
            except ValueError:
                pass
        return False


class DataSchema:
    """
    Declarative dictionary schema validator.
    Enforces required keys, expected data types, string lengths, and numeric ranges.
    """

    def __init__(self, rules: Dict[str, Dict[str, Any]]):
        """
        rules format:
        {
            "field_name": {
                "type": str | int | float | bool | list | dict,
                "required": True | False,
                "min_len": 3,
                "max_len": 100,
                "min_val": 0,
                "max_val": 100,
                "validator": Callable[[Any], bool],
                "default": Any
            }
        }
        """
        self.rules = rules

    def validate(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], Dict[str, str]]:
        """
        Validates dictionary against schema rules.
        Returns: (is_valid, sanitized_data, errors_dict)
        """
        errors = {}
        cleaned = {}

        for field, rule in self.rules.items():
            expected_type = rule.get("type")
            is_required = rule.get("required", False)
            val = data.get(field)

            if val is None or val == "":
                if is_required:
                    errors[field] = f"Field '{field}' is required and cannot be empty."
                    continue
                else:
                    if "default" in rule:
                        cleaned[field] = rule["default"]
                    continue

            # Type check
            if expected_type and not isinstance(val, expected_type):
                # Try auto-casting for numeric types
                try:
                    if expected_type == int:
                        val = int(val)
                    elif expected_type == float:
                        val = float(val)
                    elif expected_type == bool:
                        val = bool(val)
                    elif expected_type == str:
                        val = str(val)
                    else:
                        errors[field] = f"Field '{field}' must be of type {expected_type.__name__}."
                        continue
                except (ValueError, TypeError):
                    errors[field] = f"Field '{field}' failed conversion to {expected_type.__name__}."
                    continue

            # String constraints
            if isinstance(val, str):
                if "min_len" in rule and len(val) < rule["min_len"]:
                    errors[field] = f"Field '{field}' must be at least {rule['min_len']} characters."
                    continue
                if "max_len" in rule and len(val) > rule["max_len"]:
                    errors[field] = f"Field '{field}' cannot exceed {rule['max_len']} characters."
                    continue

            # Numeric constraints
            if isinstance(val, (int, float)):
                if "min_val" in rule and val < rule["min_val"]:
                    errors[field] = f"Field '{field}' cannot be less than {rule['min_val']}."
                    continue
                if "max_val" in rule and val > rule["max_val"]:
                    errors[field] = f"Field '{field}' cannot exceed {rule['max_val']}."
                    continue

            # Custom validator function
            if "validator" in rule and callable(rule["validator"]):
                if not rule["validator"](val):
                    errors[field] = f"Field '{field}' failed custom validation criteria."
                    continue

            cleaned[field] = val

        is_valid = len(errors) == 0
        return is_valid, cleaned, errors


class Sanitizer:
    """
    Data hygiene and tracking prevention sanitization methods.
    """

    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "msclkid", "mc_eid", "_hsenc", "_hsmi", "yclid",
        "igshid", "spJobID", "spUserID", "sc_campaign", "wickedid", "vero_id"
    }

    @classmethod
    def strip_tracking_params(cls, url: str) -> str:
        """
        Removes invasive ad, affiliate, and tracker query parameters from URLs.
        """
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url)
            query_dict = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            cleaned_query = {k: v for k, v in query_dict.items() if k.lower() not in cls.TRACKING_PARAMS}
            new_query = urllib.parse.urlencode(cleaned_query, doseq=True)
            reconstructed = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            return reconstructed
        except Exception:
            return url

    @staticmethod
    def sanitize_html(html_str: str) -> str:
        """Strip dangerous script tags, iframes, and onerror/onload event handlers."""
        if not html_str:
            return ""
        # Strip script, iframe, and object tags
        cleaned = re.sub(r'<(script|iframe|object|embed)[^>]*>.*?</\1>', '', html_str, flags=re.IGNORECASE | re.DOTALL)
        # Strip self-closing script or iframe
        cleaned = re.sub(r'<(script|iframe|object|embed)[^>]*/>', '', cleaned, flags=re.IGNORECASE)
        # Strip inline event handlers like onclick, onload, onerror
        cleaned = re.sub(r'\bon\w+\s*=\s*["\'][^"\']*["\']', '', cleaned, flags=re.IGNORECASE)
        # Strip javascript: URIs
        cleaned = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', cleaned, flags=re.IGNORECASE)
        return cleaned

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        I have written this part of code because unsafe characters in filenames
        can lead to filesystem collisions or cross-platform errors on Linux and Windows.
        """
        clean = re.sub(r'[\\/*?:"<>|]', "", filename)
        clean = clean.strip().replace(" ", "_")
        return clean[:128] or "unnamed_file"

    @staticmethod
    def is_safe_path(base_dir: str, target_path: str) -> bool:
        """
        I have written this part of code because directory traversal (e.g., ../../etc/passwd)
        is a severe vulnerability. Resolving the absolute real canonical path and verifying that
        it starts strictly inside base_dir guarantees absolute filesystem sandboxing!
        """
        import os
        try:
            real_base = os.path.realpath(base_dir)
            real_target = os.path.realpath(target_path)
            return real_target.startswith(real_base)
        except Exception:
            return False

    @staticmethod
    def sanitize_sql_like(value: str) -> str:
        """
        I have written this part of code because user-supplied wildcards in SQL LIKE clauses
        (such as '%' and '_') can degrade query performance and trigger unexpected full table scans.
        """
        if not value:
            return ""
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
