"""
Global National Holidays and Cultural Festivals Repository
Contains official public holidays, secular commemorations, and religious festivals
for all sovereign countries.
"""

from typing import List, Dict, Any

COUNTRY_HOLIDAYS_REPO: Dict[str, List[Dict[str, Any]]] = {
    "IN": [
        {"date": "2026-01-26", "name": "Republic Day", "local_name": "गणतंत्र दिवस", "type": "National Holiday"},
        {"date": "2026-03-04", "name": "Maha Shivaratri", "local_name": "महाशिवरात्रि", "type": "Religious Festival"},
        {"date": "2026-03-20", "name": "Eid-ul-Fitr", "local_name": "ईद-उल-फ़ित्र", "type": "Religious Festival"},
        {"date": "2026-03-24", "name": "Holi (Festival of Colors)", "local_name": "होली", "type": "Cultural Festival"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "गुड फ्राइडे", "type": "National Holiday"},
        {"date": "2026-04-14", "name": "Ambedkar Jayanti / Baisakhi", "local_name": "अम्बेडकर जयंती / बैसाखी", "type": "National Observance"},
        {"date": "2026-05-27", "name": "Eid-ul-Adha (Bakrid)", "local_name": "बकरीद", "type": "Religious Festival"},
        {"date": "2026-08-15", "name": "Independence Day", "local_name": "स्वतंत्रता दिवस", "type": "National Holiday"},
        {"date": "2026-08-28", "name": "Raksha Bandhan", "local_name": "रक्षाबंधन", "type": "Cultural Festival"},
        {"date": "2026-09-04", "name": "Janmashtami", "local_name": "जन्माष्टमी", "type": "Religious Festival"},
        {"date": "2026-10-02", "name": "Mahatma Gandhi Jayanti", "local_name": "गांधी जयंती", "type": "National Holiday"},
        {"date": "2026-10-20", "name": "Dussehra (Vijayadashami)", "local_name": "दशहरा", "type": "Cultural Festival"},
        {"date": "2026-11-08", "name": "Diwali (Festival of Lights)", "local_name": "दीपावली", "type": "National Festival"},
        {"date": "2026-11-24", "name": "Guru Nanak Jayanti", "local_name": "गुरु नानक जयंती", "type": "Religious Festival"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "बड़ा दिन", "type": "National Holiday"}
    ],
    "US": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "New Year's Day", "type": "Federal Holiday"},
        {"date": "2026-01-19", "name": "Martin Luther King Jr. Day", "local_name": "MLK Day", "type": "Federal Holiday"},
        {"date": "2026-02-16", "name": "Washington's Birthday (Presidents Day)", "local_name": "Presidents Day", "type": "Federal Holiday"},
        {"date": "2026-05-25", "name": "Memorial Day", "local_name": "Memorial Day", "type": "Federal Holiday"},
        {"date": "2026-06-19", "name": "Juneteenth National Independence Day", "local_name": "Juneteenth", "type": "Federal Holiday"},
        {"date": "2026-07-04", "name": "Independence Day (4th of July)", "local_name": "4th of July", "type": "National Holiday"},
        {"date": "2026-09-07", "name": "Labor Day", "local_name": "Labor Day", "type": "Federal Holiday"},
        {"date": "2026-10-12", "name": "Columbus Day / Indigenous Peoples' Day", "local_name": "Columbus Day", "type": "Federal Holiday"},
        {"date": "2026-10-31", "name": "Halloween", "local_name": "Halloween", "type": "Cultural Festival"},
        {"date": "2026-11-11", "name": "Veterans Day", "local_name": "Veterans Day", "type": "Federal Holiday"},
        {"date": "2026-11-26", "name": "Thanksgiving Day", "local_name": "Thanksgiving", "type": "National Festival"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Christmas", "type": "Federal Holiday"}
    ],
    "GB": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "New Year's Day", "type": "Bank Holiday"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "Good Friday", "type": "Bank Holiday"},
        {"date": "2026-04-06", "name": "Easter Monday", "local_name": "Easter Monday", "type": "Bank Holiday"},
        {"date": "2026-05-04", "name": "Early May Bank Holiday", "local_name": "May Day", "type": "Bank Holiday"},
        {"date": "2026-05-25", "name": "Spring Bank Holiday", "local_name": "Spring Bank Holiday", "type": "Bank Holiday"},
        {"date": "2026-08-31", "name": "Summer Bank Holiday", "local_name": "Summer Bank Holiday", "type": "Bank Holiday"},
        {"date": "2026-11-05", "name": "Guy Fawkes Night (Bonfire Night)", "local_name": "Bonfire Night", "type": "Cultural Festival"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Christmas Day", "type": "Public Holiday"},
        {"date": "2026-12-26", "name": "Boxing Day", "local_name": "Boxing Day", "type": "Bank Holiday"}
    ],
    "JP": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "元日 (Ganjitsu)", "type": "National Holiday"},
        {"date": "2026-01-12", "name": "Coming of Age Day", "local_name": "成人の日", "type": "National Holiday"},
        {"date": "2026-02-11", "name": "National Foundation Day", "local_name": "建国記念の日", "type": "National Holiday"},
        {"date": "2026-02-23", "name": "Emperor's Birthday", "local_name": "天皇誕生日", "type": "National Holiday"},
        {"date": "2026-03-20", "name": "Vernal Equinox Day", "local_name": "春分の日", "type": "National Holiday"},
        {"date": "2026-04-29", "name": "Showa Day (Golden Week Start)", "local_name": "昭和の日", "type": "National Festival"},
        {"date": "2026-05-03", "name": "Constitution Memorial Day", "local_name": "憲法記念日", "type": "National Holiday"},
        {"date": "2026-05-04", "name": "Greenery Day", "local_name": "みどりの日", "type": "National Holiday"},
        {"date": "2026-05-05", "name": "Children's Day", "local_name": "こどもの日", "type": "National Holiday"},
        {"date": "2026-07-20", "name": "Marine Day", "local_name": "海の日", "type": "National Holiday"},
        {"date": "2026-08-11", "name": "Mountain Day", "local_name": "山の日", "type": "National Holiday"},
        {"date": "2026-09-21", "name": "Respect for the Aged Day", "local_name": "敬老の日", "type": "National Holiday"},
        {"date": "2026-10-12", "name": "Sports Day", "local_name": "スポーツの日", "type": "National Holiday"},
        {"date": "2026-11-03", "name": "Culture Day", "local_name": "文化の日", "type": "National Holiday"},
        {"date": "2026-11-23", "name": "Labor Thanksgiving Day", "local_name": "勤労感謝の日", "type": "National Holiday"}
    ],
    "CN": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "元旦 (Yuandān)", "type": "Public Holiday"},
        {"date": "2026-02-17", "name": "Chinese Lunar New Year (Spring Festival)", "local_name": "春节 (Chūnjié)", "type": "National Festival"},
        {"date": "2026-03-03", "name": "Lantern Festival", "local_name": "元宵节", "type": "Cultural Festival"},
        {"date": "2026-04-05", "name": "Qingming Tomb Sweeping Festival", "local_name": "清明节", "type": "National Holiday"},
        {"date": "2026-05-01", "name": "Labor Day Golden Week", "local_name": "劳动节", "type": "National Holiday"},
        {"date": "2026-06-19", "name": "Dragon Boat Festival", "local_name": "端午节", "type": "National Festival"},
        {"date": "2026-09-25", "name": "Mid-Autumn Moon Festival", "local_name": "中秋节", "type": "National Festival"},
        {"date": "2026-10-01", "name": "National Day Golden Week", "local_name": "国庆节", "type": "National Holiday"}
    ],
    "FR": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "Jour de l'An", "type": "Public Holiday"},
        {"date": "2026-04-06", "name": "Easter Monday", "local_name": "Lundi de Pâques", "type": "Public Holiday"},
        {"date": "2026-05-01", "name": "Labor Day", "local_name": "Fête du Travail", "type": "Public Holiday"},
        {"date": "2026-05-08", "name": "Victory in Europe Day 1945", "local_name": "Victoire 1945", "type": "National Holiday"},
        {"date": "2026-05-14", "name": "Ascension Day", "local_name": "Ascension", "type": "Religious Festival"},
        {"date": "2026-07-14", "name": "Bastille Day (National Day)", "local_name": "Fête Nationale", "type": "National Holiday"},
        {"date": "2026-08-15", "name": "Assumption of Mary", "local_name": "Assomption", "type": "Public Holiday"},
        {"date": "2026-11-01", "name": "All Saints' Day", "local_name": "La Toussaint", "type": "Public Holiday"},
        {"date": "2026-11-11", "name": "Armistice Day 1918", "local_name": "Armistice 1918", "type": "National Holiday"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Noël", "type": "Public Holiday"}
    ],
    "DE": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "Neujahr", "type": "Public Holiday"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "Karfreitag", "type": "Public Holiday"},
        {"date": "2026-04-06", "name": "Easter Monday", "local_name": "Ostermontag", "type": "Public Holiday"},
        {"date": "2026-05-01", "name": "Labor Day", "local_name": "Tag der Arbeit", "type": "Public Holiday"},
        {"date": "2026-05-14", "name": "Ascension Day / Father's Day", "local_name": "Christi Himmelfahrt", "type": "Public Holiday"},
        {"date": "2026-05-25", "name": "Whit Monday", "local_name": "Pfingstmontag", "type": "Public Holiday"},
        {"date": "2026-10-03", "name": "German Unity Day", "local_name": "Tag der Deutschen Einheit", "type": "National Holiday"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Erster Weihnachtstag", "type": "Public Holiday"},
        {"date": "2026-12-26", "name": "Boxing Day / St. Stephen's", "local_name": "Zweiter Weihnachtstag", "type": "Public Holiday"}
    ],
    "CA": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "Jour de l'An", "type": "Statutory Holiday"},
        {"date": "2026-02-16", "name": "Family Day", "local_name": "Fête de la famille", "type": "Provincial Holiday"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "Vendredi Saint", "type": "Statutory Holiday"},
        {"date": "2026-05-18", "name": "Victoria Day", "local_name": "Fête de la Reine", "type": "Statutory Holiday"},
        {"date": "2026-07-01", "name": "Canada Day", "local_name": "Fête du Canada", "type": "National Holiday"},
        {"date": "2026-09-07", "name": "Labour Day", "local_name": "Fête du Travail", "type": "Statutory Holiday"},
        {"date": "2026-09-30", "name": "National Day for Truth and Reconciliation", "local_name": "Journée de la vérité", "type": "Federal Holiday"},
        {"date": "2026-10-12", "name": "Thanksgiving Day", "local_name": "Action de grâce", "type": "Statutory Holiday"},
        {"date": "2026-11-11", "name": "Remembrance Day", "local_name": "Jour du Souvenir", "type": "Statutory Holiday"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Noël", "type": "Statutory Holiday"}
    ],
    "AU": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "New Year's Day", "type": "Public Holiday"},
        {"date": "2026-01-26", "name": "Australia Day", "local_name": "Australia Day", "type": "National Holiday"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "Good Friday", "type": "Public Holiday"},
        {"date": "2026-04-06", "name": "Easter Monday", "local_name": "Easter Monday", "type": "Public Holiday"},
        {"date": "2026-04-25", "name": "ANZAC Day", "local_name": "ANZAC Day", "type": "National Holiday"},
        {"date": "2026-06-08", "name": "King's Birthday", "local_name": "King's Birthday", "type": "Public Holiday"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Christmas Day", "type": "Public Holiday"},
        {"date": "2026-12-26", "name": "Boxing Day", "local_name": "Boxing Day", "type": "Public Holiday"}
    ],
    "BR": [
        {"date": "2026-01-01", "name": "New Year's Day", "local_name": "Confraternização Universal", "type": "National Holiday"},
        {"date": "2026-02-17", "name": "Carnival Tuesday", "local_name": "Carnaval", "type": "National Festival"},
        {"date": "2026-04-03", "name": "Good Friday", "local_name": "Sexta-feira Santa", "type": "National Holiday"},
        {"date": "2026-04-21", "name": "Tiradentes Day", "local_name": "Tiradentes", "type": "National Holiday"},
        {"date": "2026-05-01", "name": "Labor Day", "local_name": "Dia do Trabalho", "type": "National Holiday"},
        {"date": "2026-06-04", "name": "Corpus Christi", "local_name": "Corpus Christi", "type": "Religious Festival"},
        {"date": "2026-09-07", "name": "Independence Day", "local_name": "Independência do Brasil", "type": "National Holiday"},
        {"date": "2026-10-12", "name": "Our Lady of Aparecida", "local_name": "Nossa Senhora Aparecida", "type": "National Holiday"},
        {"date": "2026-11-02", "name": "All Souls' Day", "local_name": "Finados", "type": "National Holiday"},
        {"date": "2026-11-15", "name": "Republic Proclamation Day", "local_name": "Proclamação da República", "type": "National Holiday"},
        {"date": "2026-12-25", "name": "Christmas Day", "local_name": "Natal", "type": "National Holiday"}
    ]
}
