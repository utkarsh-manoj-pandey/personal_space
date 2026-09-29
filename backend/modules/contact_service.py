"""
Contact Manager Subsystem Service
Encrypted, completely offline personal relationship management vault.
Features:
- RFC 2426 (vCard 3.0) and RFC 6350 (vCard 4.0) profile serializer and parser.
- Duplicate Contact Identification Engine: Jaro-Winkler fuzzy name matching and email deduplication.
- Interaction History & Communication Timeline Tracker.
- Categorization across VIP, Professional, Emergency, and Personal channels.
- Persistent contact directory in contacts.db.
"""

from typing import List, Dict, Any, Optional
from ..database_manager import db_manager
from ..core.algorithms import jaro_winkler_similarity
from ..core.export_engine import VCardExporter


class ContactService:
    DB = "contacts.db"

    CATEGORIES = ["Personal", "Family", "Professional", "Emergency", "VIP"]

    def __init__(self):
        self._seed_default_contacts()

    def _seed_default_contacts(self):
        """Seed initial directory entries if empty."""
        count = db_manager.execute_query(self.DB, "SELECT COUNT(*) as count FROM contacts")
        if count and count[0]["count"] == 0:
            contacts = [
                (
                    "Elena", "Rostova", "Helios Quantum Labs", "Chief Cryptographic Engineer",
                    "+1 (555) 839-2041", "+1 (555) 839-2042",
                    "elena.rostova@helios.local", "rostova.research@quantum.ch",
                    "Bahnhofstrasse 45, Zurich, Switzerland", "https://helios-quantum.ch",
                    "VIP", "Key contact for zero-knowledge cryptographic protocol reviews.",
                    "1988-11-14", 1
                ),
                (
                    "Marcus", "Vance", "Vance Strategic Intelligence", "Operations Director",
                    "+44 20 7946 0912", "",
                    "m.vance@strategic-vance.uk", "",
                    "10 Downing Enclave, London, UK", "https://strategic-vance.uk",
                    "Professional", "Consultant for subsea cable infrastructure and satellite ephemeris data.",
                    "1982-04-03", 1
                ),
                (
                    "Kenji", "Takahashi", "Neo-Kyoto Cybernetics", "Systems Architect",
                    "+81 3 5555 0143", "",
                    "kenji@cybernetics.tokyo.jp", "",
                    "Chiyoda-ku, Tokyo, Japan", "https://cybernetics.tokyo.jp",
                    "Personal", "Collaborator on local deterministic minimax game engines.",
                    "1991-08-22", 0
                )
            ]

            for c in contacts:
                db_manager.execute_non_query(
                    self.DB,
                    """INSERT INTO contacts 
                       (first_name, last_name, organization, job_title, phone_primary, phone_secondary,
                        email_primary, email_secondary, address, website, relationship_category, notes, birthday, is_favorite)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    c
                )

    def list_contacts(self, search: str = "", category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List contacts ordered by favorite status and name."""
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        if category and category != "All":
            query += " AND relationship_category = ?"
            params.append(category)
        if search:
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR organization LIKE ? OR email_primary LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term, term])
        query += " ORDER BY is_favorite DESC, last_name ASC, first_name ASC"
        return db_manager.execute_query(self.DB, query, tuple(params))

    def get_contact(self, contact_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve complete contact profile including interaction logs."""
        rows = db_manager.execute_query(self.DB, "SELECT * FROM contacts WHERE id = ?", (contact_id,))
        if not rows:
            return None
        contact = dict(rows[0])
        logs = db_manager.execute_query(
            self.DB,
            "SELECT * FROM contact_logs WHERE contact_id = ? ORDER BY logged_at DESC",
            (contact_id,)
        )
        contact["logs"] = logs
        return contact

    def create_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact entry."""
        new_id = db_manager.execute_non_query(
            self.DB,
            """INSERT INTO contacts 
               (first_name, last_name, organization, job_title, phone_primary, phone_secondary,
                email_primary, email_secondary, address, website, relationship_category, notes, birthday, is_favorite)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("first_name", "Anonymous").strip(),
                data.get("last_name", "").strip(),
                data.get("organization", "").strip(),
                data.get("job_title", "").strip(),
                data.get("phone_primary", "").strip(),
                data.get("phone_secondary", "").strip(),
                data.get("email_primary", "").strip(),
                data.get("email_secondary", "").strip(),
                data.get("address", "").strip(),
                data.get("website", "").strip(),
                data.get("relationship_category", "Personal"),
                data.get("notes", "").strip(),
                data.get("birthday", ""),
                1 if data.get("is_favorite") else 0
            )
        )
        return self.get_contact(new_id) or {"id": new_id, "first_name": data.get("first_name", "")}

    def update_contact(self, contact_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update contact profile."""
        existing = self.get_contact(contact_id)
        if not existing:
            return None

        db_manager.execute_non_query(
            self.DB,
            """UPDATE contacts SET
               first_name = ?, last_name = ?, organization = ?, job_title = ?,
               phone_primary = ?, phone_secondary = ?, email_primary = ?, email_secondary = ?,
               address = ?, website = ?, relationship_category = ?, notes = ?,
               birthday = ?, is_favorite = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                data.get("first_name", existing["first_name"]).strip(),
                data.get("last_name", existing["last_name"]).strip(),
                data.get("organization", existing["organization"]).strip(),
                data.get("job_title", existing["job_title"]).strip(),
                data.get("phone_primary", existing["phone_primary"]).strip(),
                data.get("phone_secondary", existing["phone_secondary"]).strip(),
                data.get("email_primary", existing["email_primary"]).strip(),
                data.get("email_secondary", existing["email_secondary"]).strip(),
                data.get("address", existing["address"]).strip(),
                data.get("website", existing["website"]).strip(),
                data.get("relationship_category", existing["relationship_category"]),
                data.get("notes", existing["notes"]).strip(),
                data.get("birthday", existing["birthday"]),
                1 if data.get("is_favorite", existing["is_favorite"]) else 0,
                contact_id
            )
        )
        return self.get_contact(contact_id)

    def delete_contact(self, contact_id: int) -> bool:
        """Delete contact entry."""
        return db_manager.execute_non_query(self.DB, "DELETE FROM contacts WHERE id = ?", (contact_id,)) > 0

    def add_interaction_log(self, contact_id: int, log_type: str, summary: str) -> Dict[str, Any]:
        """Record an interaction event (Call, Meeting, Email, Security Note)."""
        new_id = db_manager.execute_non_query(
            self.DB,
            "INSERT INTO contact_logs (contact_id, log_type, summary) VALUES (?, ?, ?)",
            (contact_id, log_type.strip(), summary.strip())
        )
        rows = db_manager.execute_query(self.DB, "SELECT * FROM contact_logs WHERE id = ?", (new_id,))
        return rows[0] if rows else {}

    def find_duplicate_candidates(self) -> List[Dict[str, Any]]:
        """
        Uses Jaro-Winkler fuzzy string similarity and email equality to detect duplicate entries.
        """
        contacts = self.list_contacts()
        duplicates = []

        for i in range(len(contacts)):
            for j in range(i + 1, len(contacts)):
                c1 = contacts[i]
                c2 = contacts[j]

                name1 = f"{c1.get('first_name', '')} {c1.get('last_name', '')}".strip().lower()
                name2 = f"{c2.get('first_name', '')} {c2.get('last_name', '')}".strip().lower()

                sim = jaro_winkler_similarity(name1, name2)
                email_match = (
                    bool(c1.get("email_primary")) and
                    c1.get("email_primary").lower() == c2.get("email_primary", "").lower()
                )

                if sim >= 0.88 or email_match:
                    duplicates.append({
                        "contact_a": {"id": c1["id"], "name": name1, "email": c1.get("email_primary")},
                        "contact_b": {"id": c2["id"], "name": name2, "email": c2.get("email_primary")},
                        "similarity_score": sim,
                        "email_match": email_match
                    })

        return duplicates

    def export_vcard(self, contact_id: int) -> str:
        """Export contact profile in RFC 2426 vCard 3.0 format."""
        contact = self.get_contact(contact_id)
        if not contact:
            return ""
        return VCardExporter.serialize_vcard(contact)


contact_service = ContactService()
