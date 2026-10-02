"""
Comprehensive Geopolitical Database of Sovereign Nations & Territories
Contains 200+ sovereign nations with exact geospatial coordinates, capitals, ISO codes,
populations, currencies, UTC offsets, strategic alliances, defense postures, and assets.
"""

from typing import List, Dict, Any

ALL_COUNTRIES_DATA: List[Dict[str, Any]] = [
    {
        "id": "US", "iso3": "USA", "name": "United States", "official_name": "United States",
        "flag": "US", "capital": "Washington, D.C.", "region": "North America", "subregion": "North America",
        "lat": 38.8951, "lon": -77.0364, "population": 339900000, "area_sq_km": 9833517,
        "currency_code": "USD", "currency_symbol": "$", "currency_name": "US Dollar",
        "languages": ["English"], "utc_offset": -5.0,
        "alliances": ["NATO", "Five Eyes", "G7", "Quad", "AUKUS"], "strategic_assets": ["Norfolk Naval Base", "GPS Constellation", "Silicon Valley Tech Base"],
        "military_active": "1.39M Active", "defense_budget": "86B", "cyber_readiness": 96,
        "geopolitical_summary": "Global superpower leading Western collective defense, primary dollar reserve currency issuer."
    },
    {
        "id": "CA", "iso3": "CAN", "name": "Canada", "official_name": "Canada",
        "flag": "CA", "capital": "Ottawa", "region": "North America", "subregion": "North America",
        "lat": 45.4215, "lon": -75.6972, "population": 40500000, "area_sq_km": 9984670,
        "currency_code": "CAD", "currency_symbol": "C$", "currency_name": "Canadian Dollar",
        "languages": ["English", "French"], "utc_offset": -5.0,
        "alliances": ["NORAD", "NATO", "Five Eyes", "G7"], "strategic_assets": ["Northwest Passage", "Alberta Oil Sands", "Critical Minerals Belt"],
        "military_active": "68,000 Active", "defense_budget": "9B", "cyber_readiness": 88,
        "geopolitical_summary": "Arctic and North American continental defense partner, premier supplier of uranium and potash."
    },
    {
        "id": "MX", "iso3": "MEX", "name": "Mexico", "official_name": "Mexico",
        "flag": "MX", "capital": "Mexico City", "region": "North America", "subregion": "North America",
        "lat": 19.4326, "lon": -99.1332, "population": 129800000, "area_sq_km": 1964375,
        "currency_code": "MXN", "currency_symbol": "$", "currency_name": "Mexican Peso",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["USMCA", "G20", "Pacific Alliance"], "strategic_assets": ["Isthmus of Tehuantepec Corridor", "Gulf Oil Reserves"],
        "military_active": "277,000 Active", "defense_budget": ".8B", "cyber_readiness": 72,
        "geopolitical_summary": "Critical North American manufacturing nexus, interoceanic trade bridge between Atlantic and Pacific."
    },
    {
        "id": "CU", "iso3": "CUB", "name": "Cuba", "official_name": "Cuba",
        "flag": "CU", "capital": "Havana", "region": "North America", "subregion": "North America",
        "lat": 23.1136, "lon": -82.3666, "population": 11200000, "area_sq_km": 109884,
        "currency_code": "CUP", "currency_symbol": "$", "currency_name": "Cuban Peso",
        "languages": ["Spanish"], "utc_offset": -5.0,
        "alliances": ["ALBA", "CELAC"], "strategic_assets": ["Straits of Florida Gate", "Mariel Port"],
        "military_active": "49,000 Active", "defense_budget": ".2B", "cyber_readiness": 60,
        "geopolitical_summary": "Strategically positioned at entry to Gulf of Mexico, Caribbean sovereign island nation."
    },
    {
        "id": "PA", "iso3": "PAN", "name": "Panama", "official_name": "Panama",
        "flag": "PA", "capital": "Panama City", "region": "North America", "subregion": "North America",
        "lat": 8.9824, "lon": -79.5199, "population": 4400000, "area_sq_km": 75417,
        "currency_code": "USD", "currency_symbol": "$", "currency_name": "US Dollar / Balboa",
        "languages": ["Spanish"], "utc_offset": -5.0,
        "alliances": ["SICA", "OAS"], "strategic_assets": ["Panama Canal", "Colon Free Zone"],
        "military_active": "Police 26,000", "defense_budget": "00M", "cyber_readiness": 68,
        "geopolitical_summary": "Gatekeeper of the Panama Canal, facilitating global maritime commerce."
    },
    {
        "id": "CR", "iso3": "CRI", "name": "Costa Rica", "official_name": "Costa Rica",
        "flag": "CR", "capital": "San Jose", "region": "North America", "subregion": "North America",
        "lat": 9.9281, "lon": -84.0907, "population": 5200000, "area_sq_km": 51100,
        "currency_code": "CRC", "currency_symbol": "\u20a1", "currency_name": "Costa Rican Colon",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["OECD", "SICA"], "strategic_assets": ["Semiconductor Assembly Hub", "Renewable Grid"],
        "military_active": "No Standing Military", "defense_budget": "50M", "cyber_readiness": 75,
        "geopolitical_summary": "Democracy with no standing army since 1948, tech exporter and green energy leader."
    },
    {
        "id": "JM", "iso3": "JAM", "name": "Jamaica", "official_name": "Jamaica",
        "flag": "JM", "capital": "Kingston", "region": "North America", "subregion": "North America",
        "lat": 17.9712, "lon": -76.7936, "population": 2800000, "area_sq_km": 10991,
        "currency_code": "JMD", "currency_symbol": "J$", "currency_name": "Jamaican Dollar",
        "languages": ["English"], "utc_offset": -5.0,
        "alliances": ["CARICOM", "Commonwealth"], "strategic_assets": ["Kingston Transshipment Hub"],
        "military_active": "4,000 Active", "defense_budget": "20M", "cyber_readiness": 62,
        "geopolitical_summary": "Major maritime transshipment hub in the central Caribbean basin."
    },
    {
        "id": "DO", "iso3": "DOM", "name": "Dominican Republic", "official_name": "Dominican Republic",
        "flag": "DO", "capital": "Santo Domingo", "region": "North America", "subregion": "North America",
        "lat": 18.4861, "lon": -69.9312, "population": 11300000, "area_sq_km": 48671,
        "currency_code": "DOP", "currency_symbol": "RD$", "currency_name": "Dominican Peso",
        "languages": ["Spanish"], "utc_offset": -4.0,
        "alliances": ["DR-CAFTA", "CELAC"], "strategic_assets": ["Caucedo Megaport", "Pueblo Viejo Gold"],
        "military_active": "56,000 Active", "defense_budget": "80M", "cyber_readiness": 65,
        "geopolitical_summary": "Largest economy in the Caribbean and Central America."
    },
    {
        "id": "GT", "iso3": "GTM", "name": "Guatemala", "official_name": "Guatemala",
        "flag": "GT", "capital": "Guatemala City", "region": "North America", "subregion": "North America",
        "lat": 14.6349, "lon": -90.5069, "population": 18000000, "area_sq_km": 108889,
        "currency_code": "GTQ", "currency_symbol": "Q", "currency_name": "Guatemalan Quetzal",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["SICA", "OAS"], "strategic_assets": ["Puerto Quetzal", "Santo Tomas Port"],
        "military_active": "21,500 Active", "defense_budget": "10M", "cyber_readiness": 58,
        "geopolitical_summary": "Most populous Central American state, critical land bridge."
    },
    {
        "id": "HN", "iso3": "HND", "name": "Honduras", "official_name": "Honduras",
        "flag": "HN", "capital": "Tegucigalpa", "region": "North America", "subregion": "North America",
        "lat": 14.0723, "lon": -87.1921, "population": 10400000, "area_sq_km": 112492,
        "currency_code": "HNL", "currency_symbol": "L", "currency_name": "Honduran Lempira",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["SICA"], "strategic_assets": ["Puerto Cortes Deepwater Port"],
        "military_active": "16,000 Active", "defense_budget": "80M", "cyber_readiness": 52,
        "geopolitical_summary": "Key Central American trade hub with premier Atlantic deepwater port."
    },
    {
        "id": "SV", "iso3": "SLV", "name": "El Salvador", "official_name": "El Salvador",
        "flag": "SV", "capital": "San Salvador", "region": "North America", "subregion": "North America",
        "lat": 13.6929, "lon": -89.2182, "population": 6350000, "area_sq_km": 21041,
        "currency_code": "USD", "currency_symbol": "$", "currency_name": "US Dollar",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["SICA"], "strategic_assets": ["Acajutla Port", "Geothermal Energy Grid"],
        "military_active": "24,500 Active", "defense_budget": "50M", "cyber_readiness": 64,
        "geopolitical_summary": "Pacific coastal Central American nation pioneering geothermal energy."
    },
    {
        "id": "NI", "iso3": "NIC", "name": "Nicaragua", "official_name": "Nicaragua",
        "flag": "NI", "capital": "Managua", "region": "North America", "subregion": "North America",
        "lat": 12.115, "lon": -86.2362, "population": 7000000, "area_sq_km": 130373,
        "currency_code": "NIO", "currency_symbol": "C$", "currency_name": "Nicaraguan Cordoba",
        "languages": ["Spanish"], "utc_offset": -6.0,
        "alliances": ["ALBA"], "strategic_assets": ["Lake Nicaragua", "Corinto Port"],
        "military_active": "12,000 Active", "defense_budget": "0M", "cyber_readiness": 48,
        "geopolitical_summary": "Largest geographic territory in Central America."
    },
    {
        "id": "BS", "iso3": "BHS", "name": "Bahamas", "official_name": "Bahamas",
        "flag": "BS", "capital": "Nassau", "region": "North America", "subregion": "North America",
        "lat": 25.0343, "lon": -77.3963, "population": 410000, "area_sq_km": 13943,
        "currency_code": "BSD", "currency_symbol": "$", "currency_name": "Bahamian Dollar",
        "languages": ["English"], "utc_offset": -5.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Freeport Container Port", "Offshore Banking"],
        "military_active": "1,500 Active", "defense_budget": "0M", "cyber_readiness": 65,
        "geopolitical_summary": "Archipelagic nation commanding Florida Straits maritime approaches."
    },
    {
        "id": "TT", "iso3": "TTO", "name": "Trinidad and Tobago", "official_name": "Trinidad and Tobago",
        "flag": "TT", "capital": "Port of Spain", "region": "North America", "subregion": "North America",
        "lat": 10.6549, "lon": -61.5019, "population": 1530000, "area_sq_km": 5131,
        "currency_code": "TTD", "currency_symbol": "TT$", "currency_name": "Trinidad & Tobago Dollar",
        "languages": ["English"], "utc_offset": -4.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Point Lisas Petrochemical Hub", "LNG Terminals"],
        "military_active": "4,000 Active", "defense_budget": "50M", "cyber_readiness": 70,
        "geopolitical_summary": "Foremost natural gas and petrochemical exporter in the Caribbean."
    },
    {
        "id": "BB", "iso3": "BRB", "name": "Barbados", "official_name": "Barbados",
        "flag": "BB", "capital": "Bridgetown", "region": "North America", "subregion": "North America",
        "lat": 13.1939, "lon": -59.5432, "population": 281000, "area_sq_km": 430,
        "currency_code": "BBD", "currency_symbol": "Bds$", "currency_name": "Barbados Dollar",
        "languages": ["English"], "utc_offset": -4.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Deepwater Harbor", "International Business"],
        "military_active": "600 Active", "defense_budget": "5M", "cyber_readiness": 68,
        "geopolitical_summary": "Easternmost Caribbean island state with high governance stability."
    },
    {
        "id": "HT", "iso3": "HTI", "name": "Haiti", "official_name": "Haiti",
        "flag": "HT", "capital": "Port-au-Prince", "region": "North America", "subregion": "North America",
        "lat": 18.5944, "lon": -72.3074, "population": 11700000, "area_sq_km": 27750,
        "currency_code": "HTG", "currency_symbol": "G", "currency_name": "Haitian Gourde",
        "languages": ["French", "Haitian Creole"], "utc_offset": -5.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Windward Passage Sentinel"],
        "military_active": "2,000 Active", "defense_budget": "0M", "cyber_readiness": 35,
        "geopolitical_summary": "Strategically occupies western Hispaniola along the Windward Passage."
    },
    {
        "id": "BZ", "iso3": "BLZ", "name": "Belize", "official_name": "Belize",
        "flag": "BZ", "capital": "Belmopan", "region": "North America", "subregion": "North America",
        "lat": 17.251, "lon": -88.759, "population": 405000, "area_sq_km": 22966,
        "currency_code": "BZD", "currency_symbol": "BZ$", "currency_name": "Belize Dollar",
        "languages": ["English"], "utc_offset": -6.0,
        "alliances": ["CARICOM", "SICA"], "strategic_assets": ["Belize Barrier Reef", "Sugar Agro-industry"],
        "military_active": "1,500 Active", "defense_budget": "5M", "cyber_readiness": 56,
        "geopolitical_summary": "Only English-speaking nation in Central America."
    },
    {
        "id": "BR", "iso3": "BRA", "name": "Brazil", "official_name": "Brazil",
        "flag": "BR", "capital": "Brasilia", "region": "South America", "subregion": "South America",
        "lat": -15.8267, "lon": -47.9218, "population": 216400000, "area_sq_km": 8515767,
        "currency_code": "BRL", "currency_symbol": "R$", "currency_name": "Brazilian Real",
        "languages": ["Portuguese"], "utc_offset": -3.0,
        "alliances": ["BRICS+", "G20", "Mercosur"], "strategic_assets": ["Santos Port", "Pre-Salt Oil Basins", "Embraer"],
        "military_active": "360,000 Active", "defense_budget": "4B", "cyber_readiness": 83,
        "geopolitical_summary": "Agricultural superpower, largest economy in South America."
    },
    {
        "id": "AR", "iso3": "ARG", "name": "Argentina", "official_name": "Argentina",
        "flag": "AR", "capital": "Buenos Aires", "region": "South America", "subregion": "South America",
        "lat": -34.6037, "lon": -58.3816, "population": 46700000, "area_sq_km": 2780400,
        "currency_code": "ARS", "currency_symbol": "$", "currency_name": "Argentine Peso",
        "languages": ["Spanish"], "utc_offset": -3.0,
        "alliances": ["G20", "Mercosur"], "strategic_assets": ["Vaca Muerta Shale", "Lithium Triangle"],
        "military_active": "84,000 Active", "defense_budget": ".2B", "cyber_readiness": 74,
        "geopolitical_summary": "Major shale energy, lithium, and agricultural exporter."
    },
    {
        "id": "CO", "iso3": "COL", "name": "Colombia", "official_name": "Colombia",
        "flag": "CO", "capital": "Bogota", "region": "South America", "subregion": "South America",
        "lat": 4.711, "lon": -74.0721, "population": 52200000, "area_sq_km": 1141748,
        "currency_code": "COP", "currency_symbol": "$", "currency_name": "Colombian Peso",
        "languages": ["Spanish"], "utc_offset": -5.0,
        "alliances": ["NATO Global Partner", "OECD"], "strategic_assets": ["Buenaventura Port", "Cartagena Gateway"],
        "military_active": "295,000 Active", "defense_budget": "0.5B", "cyber_readiness": 78,
        "geopolitical_summary": "Bi-oceanic South American nation and key security partner."
    },
    {
        "id": "CL", "iso3": "CHL", "name": "Chile", "official_name": "Chile",
        "flag": "CL", "capital": "Santiago", "region": "South America", "subregion": "South America",
        "lat": -33.4489, "lon": -70.6693, "population": 19600000, "area_sq_km": 756102,
        "currency_code": "CLP", "currency_symbol": "$", "currency_name": "Chilean Peso",
        "languages": ["Spanish"], "utc_offset": -4.0,
        "alliances": ["OECD", "Pacific Alliance"], "strategic_assets": ["Atacama Copper Mines", "Strait of Magellan"],
        "military_active": "77,000 Active", "defense_budget": ".4B", "cyber_readiness": 82,
        "geopolitical_summary": "World leader in copper and lithium extraction, guardian of Cape Horn."
    },
    {
        "id": "PE", "iso3": "PER", "name": "Peru", "official_name": "Peru",
        "flag": "PE", "capital": "Lima", "region": "South America", "subregion": "South America",
        "lat": -12.0464, "lon": -77.0428, "population": 34300000, "area_sq_km": 1285216,
        "currency_code": "PEN", "currency_symbol": "S/.", "currency_name": "Peruvian Sol",
        "languages": ["Spanish", "Quechua"], "utc_offset": -5.0,
        "alliances": ["Pacific Alliance", "CPTPP"], "strategic_assets": ["Chancay Mega-Port", "Cerro Verde Copper"],
        "military_active": "81,000 Active", "defense_budget": ".8B", "cyber_readiness": 70,
        "geopolitical_summary": "Major Pacific littoral mining giant, developing Chancay deepwater hub."
    },
    {
        "id": "VE", "iso3": "VEN", "name": "Venezuela", "official_name": "Venezuela",
        "flag": "VE", "capital": "Caracas", "region": "South America", "subregion": "South America",
        "lat": 10.4806, "lon": -66.9036, "population": 29000000, "area_sq_km": 916445,
        "currency_code": "VES", "currency_symbol": "Bs.", "currency_name": "Venezuelan Bolivar",
        "languages": ["Spanish"], "utc_offset": -4.0,
        "alliances": ["OPEC", "ALBA"], "strategic_assets": ["Orinoco Proven Crude Basins", "Guri Dam"],
        "military_active": "123,000 Active", "defense_budget": ".5B", "cyber_readiness": 63,
        "geopolitical_summary": "Possesses the largest proven crude oil reserves on planet Earth."
    },
    {
        "id": "EC", "iso3": "ECU", "name": "Ecuador", "official_name": "Ecuador",
        "flag": "EC", "capital": "Quito", "region": "South America", "subregion": "South America",
        "lat": -0.1807, "lon": -78.4678, "population": 18200000, "area_sq_km": 283561,
        "currency_code": "USD", "currency_symbol": "$", "currency_name": "US Dollar",
        "languages": ["Spanish"], "utc_offset": -5.0,
        "alliances": ["Andean Community"], "strategic_assets": ["Guayaquil Port", "Galapagos EEZ"],
        "military_active": "40,000 Active", "defense_budget": ".4B", "cyber_readiness": 66,
        "geopolitical_summary": "Dollarized economy, major banana, shrimp, and oil producer."
    },
    {
        "id": "BO", "iso3": "BOL", "name": "Bolivia", "official_name": "Bolivia",
        "flag": "BO", "capital": "Sucre / La Paz", "region": "South America", "subregion": "South America",
        "lat": -16.5, "lon": -68.15, "population": 12400000, "area_sq_km": 1098581,
        "currency_code": "BOB", "currency_symbol": "Bs", "currency_name": "Bolivian Boliviano",
        "languages": ["Spanish", "Quechua"], "utc_offset": -4.0,
        "alliances": ["Mercosur"], "strategic_assets": ["Salar de Uyuni Lithium (21M tons)"],
        "military_active": "35,000 Active", "defense_budget": "00M", "cyber_readiness": 55,
        "geopolitical_summary": "Landlocked heart of South America with vast lithium deposits."
    },
    {
        "id": "UY", "iso3": "URY", "name": "Uruguay", "official_name": "Uruguay",
        "flag": "UY", "capital": "Montevideo", "region": "South America", "subregion": "South America",
        "lat": -34.9011, "lon": -56.1645, "population": 3500000, "area_sq_km": 176215,
        "currency_code": "UYU", "currency_symbol": "", "currency_name": "Uruguayan Peso",
        "languages": ["Spanish"], "utc_offset": -3.0,
        "alliances": ["Mercosur", "OAS"], "strategic_assets": ["Montevideo Port", "Renewable Grid (98%)"],
        "military_active": "14,000 Active", "defense_budget": ".2B", "cyber_readiness": 84,
        "geopolitical_summary": "Pivotal Southern Cone financial and tech hub, green energy leader."
    },
    {
        "id": "PY", "iso3": "PRY", "name": "Paraguay", "official_name": "Paraguay",
        "flag": "PY", "capital": "Asuncion", "region": "South America", "subregion": "South America",
        "lat": -25.2637, "lon": -57.5759, "population": 7500000, "area_sq_km": 406752,
        "currency_code": "PYG", "currency_symbol": "\u20b2", "currency_name": "Paraguayan Guarani",
        "languages": ["Spanish", "Guarani"], "utc_offset": -4.0,
        "alliances": ["Mercosur"], "strategic_assets": ["Itaipu Hydroelectric Dam (14 GW)"],
        "military_active": "16,000 Active", "defense_budget": "20M", "cyber_readiness": 58,
        "geopolitical_summary": "Net clean energy exporter co-owning Itaipu Dam, soy producer."
    },
    {
        "id": "GY", "iso3": "GUY", "name": "Guyana", "official_name": "Guyana",
        "flag": "GY", "capital": "Georgetown", "region": "South America", "subregion": "South America",
        "lat": 6.8013, "lon": -58.1551, "population": 810000, "area_sq_km": 214969,
        "currency_code": "GYD", "currency_symbol": "G$", "currency_name": "Guyanese Dollar",
        "languages": ["English"], "utc_offset": -4.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Stabroek Offshore Oil Block (11B bbl)"],
        "military_active": "4,500 Active", "defense_budget": "20M", "cyber_readiness": 60,
        "geopolitical_summary": "Fastest growing economy globally due to massive offshore crude reserves."
    },
    {
        "id": "SR", "iso3": "SUR", "name": "Suriname", "official_name": "Suriname",
        "flag": "SR", "capital": "Paramaribo", "region": "South America", "subregion": "South America",
        "lat": 5.852, "lon": -55.2038, "population": 620000, "area_sq_km": 163820,
        "currency_code": "SRD", "currency_symbol": "$", "currency_name": "Surinamese Dollar",
        "languages": ["Dutch"], "utc_offset": -3.0,
        "alliances": ["CARICOM"], "strategic_assets": ["Offshore Oil Basins", "Gold Reserves"],
        "military_active": "2,500 Active", "defense_budget": "5M", "cyber_readiness": 55,
        "geopolitical_summary": "High forest cover, emerging offshore Guyana-Suriname basin energy producer."
    },
    {
        "id": "GB", "iso3": "GBR", "name": "United Kingdom", "official_name": "United Kingdom",
        "flag": "GB", "capital": "London", "region": "Europe", "subregion": "Europe",
        "lat": 51.5074, "lon": -0.1278, "population": 67800000, "area_sq_km": 242495,
        "currency_code": "GBP", "currency_symbol": "\u00a3", "currency_name": "Pound Sterling",
        "languages": ["English"], "utc_offset": 0.0,
        "alliances": ["NATO", "Five Eyes", "G7", "AUKUS", "UNSC P5"], "strategic_assets": ["London City", "Faslane Submarine Base", "GCHQ"],
        "military_active": "148,000 Active", "defense_budget": "8B", "cyber_readiness": 94,
        "geopolitical_summary": "Nuclear maritime power, European anchor of Five Eyes intelligence."
    },
    {
        "id": "FR", "iso3": "FRA", "name": "France", "official_name": "France",
        "flag": "FR", "capital": "Paris", "region": "Europe", "subregion": "Europe",
        "lat": 48.8566, "lon": 2.3522, "population": 68200000, "area_sq_km": 643801,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["French"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO", "UNSC P5", "G7"], "strategic_assets": ["Brest Nuclear Sub Base", "Ariane Spaceport", "56 Reactors"],
        "military_active": "205,000 Active", "defense_budget": "4B", "cyber_readiness": 91,
        "geopolitical_summary": "Autonomous nuclear power with independent strategic deterrent."
    },
    {
        "id": "DE", "iso3": "DEU", "name": "Germany", "official_name": "Germany",
        "flag": "DE", "capital": "Berlin", "region": "Europe", "subregion": "Europe",
        "lat": 52.52, "lon": 13.405, "population": 84400000, "area_sq_km": 357022,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["German"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO", "G7"], "strategic_assets": ["Frankfurt Internet Exchange (DE-CIX)", "Rhine Corridor"],
        "military_active": "183,000 Active", "defense_budget": "3B", "cyber_readiness": 92,
        "geopolitical_summary": "Economic powerhouse of Europe, leading precision manufacturing exporter."
    },
    {
        "id": "IT", "iso3": "ITA", "name": "Italy", "official_name": "Italy",
        "flag": "IT", "capital": "Rome", "region": "Europe", "subregion": "Europe",
        "lat": 41.9028, "lon": 12.4964, "population": 58900000, "area_sq_km": 301340,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Italian"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO", "G7"], "strategic_assets": ["Taranto Naval Base", "Sicily Chokepoint"],
        "military_active": "165,000 Active", "defense_budget": "2B", "cyber_readiness": 85,
        "geopolitical_summary": "Central Mediterranean maritime hub and precision engineering exporter."
    },
    {
        "id": "ES", "iso3": "ESP", "name": "Spain", "official_name": "Spain",
        "flag": "ES", "capital": "Madrid", "region": "Europe", "subregion": "Europe",
        "lat": 40.4168, "lon": -3.7038, "population": 48400000, "area_sq_km": 505990,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Spanish"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Rota Naval Station", "Algeciras Port"],
        "military_active": "120,000 Active", "defense_budget": "1B", "cyber_readiness": 87,
        "geopolitical_summary": "Atlantic-Mediterranean gatekeeper, host of NATO Aegis naval base."
    },
    {
        "id": "NL", "iso3": "NLD", "name": "Netherlands", "official_name": "Netherlands",
        "flag": "NL", "capital": "Amsterdam", "region": "Europe", "subregion": "Europe",
        "lat": 52.3676, "lon": 4.9041, "population": 17900000, "area_sq_km": 41543,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Dutch"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Port of Rotterdam", "ASML Semiconductor Lithography"],
        "military_active": "41,000 Active", "defense_budget": "3B", "cyber_readiness": 93,
        "geopolitical_summary": "Center of semiconductor lithography via ASML, Europe premier port."
    },
    {
        "id": "RU", "iso3": "RUS", "name": "Russia", "official_name": "Russia",
        "flag": "RU", "capital": "Moscow", "region": "Europe", "subregion": "Europe",
        "lat": 55.7558, "lon": 37.6173, "population": 144200000, "area_sq_km": 17098246,
        "currency_code": "RUB", "currency_symbol": "\u20bd", "currency_name": "Russian Ruble",
        "languages": ["Russian"], "utc_offset": 3.0,
        "alliances": ["CSTO", "BRICS+", "SCO", "UNSC P5"], "strategic_assets": ["Northern Sea Route", "Severodvinsk Shipyards", "Plesetsk"],
        "military_active": "1.32M Active", "defense_budget": "09B", "cyber_readiness": 95,
        "geopolitical_summary": "Nuclear superpower spanning 11 timezones, major energy and grain exporter."
    },
    {
        "id": "UA", "iso3": "UKR", "name": "Ukraine", "official_name": "Ukraine",
        "flag": "UA", "capital": "Kyiv", "region": "Europe", "subregion": "Europe",
        "lat": 50.4501, "lon": 30.5234, "population": 37500000, "area_sq_km": 603628,
        "currency_code": "UAH", "currency_symbol": "\u20b4", "currency_name": "Ukrainian Hryvnia",
        "languages": ["Ukrainian"], "utc_offset": 2.0,
        "alliances": ["EU Candidate", "NATO Partner"], "strategic_assets": ["Zaporizhzhia Nuclear Complex", "Odesa Black Sea Port"],
        "military_active": "850,000 Active", "defense_budget": "2B", "cyber_readiness": 89,
        "geopolitical_summary": "Eastern European frontline battleground, rapidly expanding robotic defense sector."
    },
    {
        "id": "PL", "iso3": "POL", "name": "Poland", "official_name": "Poland",
        "flag": "PL", "capital": "Warsaw", "region": "Europe", "subregion": "Europe",
        "lat": 52.2297, "lon": 21.0122, "population": 37800000, "area_sq_km": 312696,
        "currency_code": "PLN", "currency_symbol": "z\u0142", "currency_name": "Polish Zloty",
        "languages": ["Polish"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Suwalki Gap", "Gdansk Deepwater Port", "Rzeszow Logistics"],
        "military_active": "216,000 Active", "defense_budget": "5B", "cyber_readiness": 90,
        "geopolitical_summary": "NATO fastest-rearming Eastern European pillar, continental ground fortress."
    },
    {
        "id": "SE", "iso3": "SWE", "name": "Sweden", "official_name": "Sweden",
        "flag": "SE", "capital": "Stockholm", "region": "Europe", "subregion": "Europe",
        "lat": 59.3293, "lon": 18.0686, "population": 10500000, "area_sq_km": 450295,
        "currency_code": "SEK", "currency_symbol": "kr", "currency_name": "Swedish Krona",
        "languages": ["Swedish"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Gotland Island", "Saab Gripen Facilities", "Kiruna Iron Ore"],
        "military_active": "24,000 Active", "defense_budget": "2B", "cyber_readiness": 93,
        "geopolitical_summary": "New NATO Nordic pillar controlling Baltic air/sea approaches from Gotland."
    },
    {
        "id": "NO", "iso3": "NOR", "name": "Norway", "official_name": "Norway",
        "flag": "NO", "capital": "Oslo", "region": "Europe", "subregion": "Europe",
        "lat": 59.9139, "lon": 10.7522, "population": 5500000, "area_sq_km": 385207,
        "currency_code": "NOK", "currency_symbol": "kr", "currency_name": "Norwegian Krone",
        "languages": ["Norwegian"], "utc_offset": 1.0,
        "alliances": ["NATO", "EFTA"], "strategic_assets": ["North Sea Gas (Equinor)", "Svalbard Satellite Base", "Wealth Fund (.6T)"],
        "military_active": "23,000 Active", "defense_budget": ".5B", "cyber_readiness": 91,
        "geopolitical_summary": "Europe premier natural gas supplier and guardian of the Barents Sea."
    },
    {
        "id": "CH", "iso3": "CHE", "name": "Switzerland", "official_name": "Switzerland",
        "flag": "CH", "capital": "Bern", "region": "Europe", "subregion": "Europe",
        "lat": 46.948, "lon": 7.4474, "population": 8900000, "area_sq_km": 41285,
        "currency_code": "CHF", "currency_symbol": "CHF", "currency_name": "Swiss Franc",
        "languages": ["German", "French", "Italian"], "utc_offset": 1.0,
        "alliances": ["EFTA", "Neutrality"], "strategic_assets": ["Gotthard Base Tunnel", "Zurich Banking", "CERN"],
        "military_active": "140,000 Militia", "defense_budget": ".2B", "cyber_readiness": 92,
        "geopolitical_summary": "Armed neutrality citadel, premier global wealth management reserve refuge."
    },
    {
        "id": "BE", "iso3": "BEL", "name": "Belgium", "official_name": "Belgium",
        "flag": "BE", "capital": "Brussels", "region": "Europe", "subregion": "Europe",
        "lat": 50.8503, "lon": 4.3517, "population": 11800000, "area_sq_km": 30528,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Dutch", "French"], "utc_offset": 1.0,
        "alliances": ["EU HQ", "NATO HQ"], "strategic_assets": ["Port of Antwerp", "NATO & EU Headquarters", "SWIFT Network"],
        "military_active": "25,000 Active", "defense_budget": ".8B", "cyber_readiness": 88,
        "geopolitical_summary": "Political capital of the European Union and NATO, hosting SWIFT messaging."
    },
    {
        "id": "TR", "iso3": "TUR", "name": "Turkey", "official_name": "Turkey",
        "flag": "TR", "capital": "Ankara", "region": "Europe", "subregion": "Europe",
        "lat": 39.9334, "lon": 32.8597, "population": 85800000, "area_sq_km": 783562,
        "currency_code": "TRY", "currency_symbol": "\u20ba", "currency_name": "Turkish Lira",
        "languages": ["Turkish"], "utc_offset": 3.0,
        "alliances": ["NATO", "G20"], "strategic_assets": ["Bosporus & Dardanelles Straits", "Incirlik Air Base", "Baykar Drones"],
        "military_active": "425,000 Active", "defense_budget": "0B", "cyber_readiness": 86,
        "geopolitical_summary": "Transcontinental controller of Black Sea straits via Montreux Convention."
    },
    {
        "id": "GR", "iso3": "GRC", "name": "Greece", "official_name": "Greece",
        "flag": "GR", "capital": "Athens", "region": "Europe", "subregion": "Europe",
        "lat": 37.9838, "lon": 23.7275, "population": 10400000, "area_sq_km": 131957,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Greek"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["World Largest Merchant Fleet", "Souda Bay Naval Base"],
        "military_active": "130,000 Active", "defense_budget": ".5B", "cyber_readiness": 81,
        "geopolitical_summary": "Controls the largest merchant shipping fleet on Earth (>20% world tonnage)."
    },
    {
        "id": "PT", "iso3": "PRT", "name": "Portugal", "official_name": "Portugal",
        "flag": "PT", "capital": "Lisbon", "region": "Europe", "subregion": "Europe",
        "lat": 38.7223, "lon": -9.1393, "population": 10500000, "area_sq_km": 92212,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Portuguese"], "utc_offset": 0.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Azores Base (Lajes)", "Sines Subsea Cable Hub"],
        "military_active": "27,000 Active", "defense_budget": ".5B", "cyber_readiness": 82,
        "geopolitical_summary": "Westernmost European state, crucial transatlantic connectivity crossroads."
    },
    {
        "id": "AT", "iso3": "AUT", "name": "Austria", "official_name": "Austria",
        "flag": "AT", "capital": "Vienna", "region": "Europe", "subregion": "Europe",
        "lat": 48.2082, "lon": 16.3738, "population": 9100000, "area_sq_km": 83871,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["German"], "utc_offset": 1.0,
        "alliances": ["EU", "Neutrality"], "strategic_assets": ["IAEA Headquarters", "OPEC Secretariat (Vienna)"],
        "military_active": "22,000 Active", "defense_budget": ".2B", "cyber_readiness": 85,
        "geopolitical_summary": "Neutral Central European bridge, host to major UN agencies and OPEC."
    },
    {
        "id": "DK", "iso3": "DNK", "name": "Denmark", "official_name": "Denmark",
        "flag": "DK", "capital": "Copenhagen", "region": "Europe", "subregion": "Europe",
        "lat": 55.6761, "lon": 12.5683, "population": 5950000, "area_sq_km": 43094,
        "currency_code": "DKK", "currency_symbol": "kr.", "currency_name": "Danish Krone",
        "languages": ["Danish"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Danish Straits (Baltic Exit)", "Greenland Sovereign Control", "Maersk Shipping"],
        "military_active": "16,000 Active", "defense_budget": ".8B", "cyber_readiness": 91,
        "geopolitical_summary": "Controls the exit of the Baltic Sea and Greenland Arctic territory."
    },
    {
        "id": "FI", "iso3": "FIN", "name": "Finland", "official_name": "Finland",
        "flag": "FI", "capital": "Helsinki", "region": "Europe", "subregion": "Europe",
        "lat": 60.1699, "lon": 24.9384, "population": 5560000, "area_sq_km": 338424,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Finnish", "Swedish"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["1,340 km Russian Border", "Icebreaker Fleet", "Civilian Bunker Network"],
        "military_active": "24,000 Active (900k Reserves)", "defense_budget": ".7B", "cyber_readiness": 94,
        "geopolitical_summary": "NATO Nordic sentinel with Europe largest trained artillery and reserve force."
    },
    {
        "id": "IE", "iso3": "IRL", "name": "Ireland", "official_name": "Ireland",
        "flag": "IE", "capital": "Dublin", "region": "Europe", "subregion": "Europe",
        "lat": 53.3498, "lon": -6.2603, "population": 5200000, "area_sq_km": 70273,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["English", "Irish"], "utc_offset": 0.0,
        "alliances": ["EU", "Neutrality"], "strategic_assets": ["Silicon Docks Tech EMEA HQs", "Atlantic Subsea Landings"],
        "military_active": "8,500 Active", "defense_budget": ".4B", "cyber_readiness": 87,
        "geopolitical_summary": "European headquarters for global technology and pharmaceutical titans."
    },
    {
        "id": "CZ", "iso3": "CZE", "name": "Czechia", "official_name": "Czechia",
        "flag": "CZ", "capital": "Prague", "region": "Europe", "subregion": "Europe",
        "lat": 50.0755, "lon": 14.4378, "population": 10800000, "area_sq_km": 78866,
        "currency_code": "CZK", "currency_symbol": "K\u010d", "currency_name": "Czech Koruna",
        "languages": ["Czech"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Skoda Auto Manufacturing", "Defense Ammunition Consortiums"],
        "military_active": "28,000 Active", "defense_budget": ".2B", "cyber_readiness": 86,
        "geopolitical_summary": "Advanced industrial manufacturing heart of Central Europe, major defense producer."
    },
    {
        "id": "RO", "iso3": "ROU", "name": "Romania", "official_name": "Romania",
        "flag": "RO", "capital": "Bucharest", "region": "Europe", "subregion": "Europe",
        "lat": 44.4268, "lon": 26.1025, "population": 19000000, "area_sq_km": 238397,
        "currency_code": "RON", "currency_symbol": "lei", "currency_name": "Romanian Leu",
        "languages": ["Romanian"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Constanta Black Sea Port", "Mihail Kogalniceanu Air Base", "Danube Delta"],
        "military_active": "71,500 Active", "defense_budget": ".5B", "cyber_readiness": 83,
        "geopolitical_summary": "Key Black Sea NATO pillar hosting major Allied air bases and Danube transit."
    },
    {
        "id": "HU", "iso3": "HUN", "name": "Hungary", "official_name": "Hungary",
        "flag": "HU", "capital": "Budapest", "region": "Europe", "subregion": "Europe",
        "lat": 47.4979, "lon": 19.0402, "population": 9600000, "area_sq_km": 93030,
        "currency_code": "HUF", "currency_symbol": "Ft", "currency_name": "Hungarian Forint",
        "languages": ["Hungarian"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Danube Valley Automotive Corridor", "Battery Mega-factories"],
        "military_active": "37,000 Active", "defense_budget": ".1B", "cyber_readiness": 79,
        "geopolitical_summary": "Central European transit hub and major EV battery manufacturing center."
    },
    {
        "id": "CN", "iso3": "CHN", "name": "China", "official_name": "China",
        "flag": "CN", "capital": "Beijing", "region": "Asia", "subregion": "Asia",
        "lat": 39.9042, "lon": 116.4074, "population": 1411000000, "area_sq_km": 9596961,
        "currency_code": "CNY", "currency_symbol": "\u00a5", "currency_name": "Renminbi Yuan",
        "languages": ["Mandarin"], "utc_offset": 8.0,
        "alliances": ["BRICS+", "SCO", "UNSC P5"], "strategic_assets": ["Shanghai Mega-Port", "Rare Earth Monopolies", "High-Speed Rail"],
        "military_active": "2.03M Active", "defense_budget": "96B", "cyber_readiness": 97,
        "geopolitical_summary": "World foremost manufacturing superpower and leading rare earth supplier."
    },
    {
        "id": "IN", "iso3": "IND", "name": "India", "official_name": "India",
        "flag": "IN", "capital": "New Delhi", "region": "Asia", "subregion": "Asia",
        "lat": 28.6139, "lon": 77.209, "population": 1435000000, "area_sq_km": 3287263,
        "currency_code": "INR", "currency_symbol": "\u20b9", "currency_name": "Indian Rupee",
        "languages": ["Hindi", "English"], "utc_offset": 5.5,
        "alliances": ["Quad", "BRICS+", "SCO", "G20"], "strategic_assets": ["Andaman Sentinel Base", "ISRO Space Center", "Bangalore Tech Hub"],
        "military_active": "1.45M Active", "defense_budget": "3B", "cyber_readiness": 91,
        "geopolitical_summary": "Most populous nation, Indian Ocean guardian, fastest growing major economy."
    },
    {
        "id": "JP", "iso3": "JPN", "name": "Japan", "official_name": "Japan",
        "flag": "JP", "capital": "Tokyo", "region": "Asia", "subregion": "Asia",
        "lat": 35.6762, "lon": 139.6503, "population": 124500000, "area_sq_km": 377975,
        "currency_code": "JPY", "currency_symbol": "\u00a5", "currency_name": "Japanese Yen",
        "languages": ["Japanese"], "utc_offset": 9.0,
        "alliances": ["G7", "Quad", "CPTPP"], "strategic_assets": ["Yokosuka Base", "Silicon Wafers (Shin-Etsu)", "Robotics Hubs"],
        "military_active": "247,000 Active", "defense_budget": "6B", "cyber_readiness": 90,
        "geopolitical_summary": "High-tech powerhouse, semiconductor materials and robotics leader."
    },
    {
        "id": "KR", "iso3": "KOR", "name": "South Korea", "official_name": "South Korea",
        "flag": "KR", "capital": "Seoul", "region": "Asia", "subregion": "Asia",
        "lat": 37.5665, "lon": 126.978, "population": 51700000, "area_sq_km": 100210,
        "currency_code": "KRW", "currency_symbol": "\u20a9", "currency_name": "South Korean Won",
        "languages": ["Korean"], "utc_offset": 9.0,
        "alliances": ["Major Non-NATO Ally", "G20"], "strategic_assets": ["Samsung & SK Hynix DRAM", "Ulsan Shipyards"],
        "military_active": "500,000 Active", "defense_budget": "8B", "cyber_readiness": 93,
        "geopolitical_summary": "Global memory semiconductor monopoly and leading naval shipbuilder."
    },
    {
        "id": "AU", "iso3": "AUS", "name": "Australia", "official_name": "Australia",
        "flag": "AU", "capital": "Canberra", "region": "Oceania", "subregion": "Oceania",
        "lat": -35.2809, "lon": 149.13, "population": 26800000, "area_sq_km": 7692024,
        "currency_code": "AUD", "currency_symbol": "A$", "currency_name": "Australian Dollar",
        "languages": ["English"], "utc_offset": 10.0,
        "alliances": ["AUKUS", "Five Eyes", "Quad"], "strategic_assets": ["Pilbara Iron Ore", "Pine Gap Defense Base", "Lithium Mines"],
        "military_active": "59,000 Active", "defense_budget": "5B", "cyber_readiness": 94,
        "geopolitical_summary": "Continental resource fortress, premier supplier of iron ore, LNG, and lithium."
    },
    {
        "id": "SG", "iso3": "SGP", "name": "Singapore", "official_name": "Singapore",
        "flag": "SG", "capital": "Singapore", "region": "Asia", "subregion": "Asia",
        "lat": 1.3521, "lon": 103.8198, "population": 5900000, "area_sq_km": 728,
        "currency_code": "SGD", "currency_symbol": "S$", "currency_name": "Singapore Dollar",
        "languages": ["English", "Malay", "Mandarin"], "utc_offset": 8.0,
        "alliances": ["ASEAN"], "strategic_assets": ["Changi Naval Base", "Jurong Petrochemical Island", "Global Port"],
        "military_active": "72,000 Active", "defense_budget": "5B", "cyber_readiness": 96,
        "geopolitical_summary": "Premier maritime crossroads of Asia and largest global transshipment hub."
    },
    {
        "id": "ID", "iso3": "IDN", "name": "Indonesia", "official_name": "Indonesia",
        "flag": "ID", "capital": "Jakarta / Nusantara", "region": "Asia", "subregion": "Asia",
        "lat": -6.2088, "lon": 106.8456, "population": 278000000, "area_sq_km": 1904569,
        "currency_code": "IDR", "currency_symbol": "Rp", "currency_name": "Indonesian Rupiah",
        "languages": ["Indonesian"], "utc_offset": 7.0,
        "alliances": ["ASEAN", "G20"], "strategic_assets": ["Sunda & Lombok Straits", "Morowali Nickel Complex"],
        "military_active": "400,000 Active", "defense_budget": ".2B", "cyber_readiness": 77,
        "geopolitical_summary": "Archipelagic giant controlling deepwater straits, world largest nickel supplier."
    },
    {
        "id": "TW", "iso3": "TWN", "name": "Taiwan", "official_name": "Taiwan",
        "flag": "TW", "capital": "Taipei", "region": "Asia", "subregion": "Asia",
        "lat": 25.033, "lon": 121.5654, "population": 23400000, "area_sq_km": 36193,
        "currency_code": "TWD", "currency_symbol": "NT$", "currency_name": "New Taiwan Dollar",
        "languages": ["Mandarin"], "utc_offset": 8.0,
        "alliances": ["Semiconductor Leader"], "strategic_assets": ["TSMC Advanced Fabs (3nm/2nm)", "Taiwan Strait Corridor"],
        "military_active": "170,000 Active", "defense_budget": "9B", "cyber_readiness": 95,
        "geopolitical_summary": "Manufactures >90% of the world most advanced logic microchips."
    },
    {
        "id": "PH", "iso3": "PHL", "name": "Philippines", "official_name": "Philippines",
        "flag": "PH", "capital": "Manila", "region": "Asia", "subregion": "Asia",
        "lat": 14.5995, "lon": 120.9842, "population": 117000000, "area_sq_km": 300000,
        "currency_code": "PHP", "currency_symbol": "\u20b1", "currency_name": "Philippine Peso",
        "languages": ["Filipino", "English"], "utc_offset": 8.0,
        "alliances": ["ASEAN", "US-PH Defense Treaty"], "strategic_assets": ["Subic Bay Naval Haven", "Luzon Strait Chokepoint"],
        "military_active": "150,000 Active", "defense_budget": ".6B", "cyber_readiness": 75,
        "geopolitical_summary": "First Island Chain nation controlling crucial Bashi Channel sea lanes."
    },
    {
        "id": "VN", "iso3": "VNM", "name": "Vietnam", "official_name": "Vietnam",
        "flag": "VN", "capital": "Hanoi", "region": "Asia", "subregion": "Asia",
        "lat": 21.0285, "lon": 105.8542, "population": 100000000, "area_sq_km": 331212,
        "currency_code": "VND", "currency_symbol": "\u20ab", "currency_name": "Vietnamese Dong",
        "languages": ["Vietnamese"], "utc_offset": 7.0,
        "alliances": ["ASEAN"], "strategic_assets": ["Cam Ranh Deepwater Bay", "Rare Earth Reserves (2nd Largest)"],
        "military_active": "480,000 Active", "defense_budget": ".2B", "cyber_readiness": 84,
        "geopolitical_summary": "Pivotal manufacturing alternative in Asia with deepwater naval ports."
    },
    {
        "id": "TH", "iso3": "THA", "name": "Thailand", "official_name": "Thailand",
        "flag": "TH", "capital": "Bangkok", "region": "Asia", "subregion": "Asia",
        "lat": 13.7563, "lon": 100.5018, "population": 71800000, "area_sq_km": 513120,
        "currency_code": "THB", "currency_symbol": "\u0e3f", "currency_name": "Thai Baht",
        "languages": ["Thai"], "utc_offset": 7.0,
        "alliances": ["ASEAN"], "strategic_assets": ["Laem Chabang Deep Seaport", "Automotive Hub"],
        "military_active": "360,000 Active", "defense_budget": ".8B", "cyber_readiness": 78,
        "geopolitical_summary": "Central Southeast Asian manufacturing nexus, auto exporter and rice producer."
    },
    {
        "id": "MY", "iso3": "MYS", "name": "Malaysia", "official_name": "Malaysia",
        "flag": "MY", "capital": "Kuala Lumpur", "region": "Asia", "subregion": "Asia",
        "lat": 3.139, "lon": 101.6869, "population": 34000000, "area_sq_km": 330803,
        "currency_code": "MYR", "currency_symbol": "RM", "currency_name": "Malaysian Ringgit",
        "languages": ["Malay"], "utc_offset": 8.0,
        "alliances": ["ASEAN"], "strategic_assets": ["Penang Semiconductor Testing", "Port Klang"],
        "military_active": "115,000 Active", "defense_budget": ".1B", "cyber_readiness": 88,
        "geopolitical_summary": "Handles 13% of world semiconductor packaging and testing."
    },
    {
        "id": "PK", "iso3": "PAK", "name": "Pakistan", "official_name": "Pakistan",
        "flag": "PK", "capital": "Islamabad", "region": "Asia", "subregion": "Asia",
        "lat": 33.6844, "lon": 73.0479, "population": 241000000, "area_sq_km": 881913,
        "currency_code": "PKR", "currency_symbol": "\u20a8", "currency_name": "Pakistani Rupee",
        "languages": ["Urdu", "English"], "utc_offset": 5.0,
        "alliances": ["SCO"], "strategic_assets": ["Gwadar Deepwater Port (CPEC)", "Indus Basin"],
        "military_active": "654,000 Active", "defense_budget": "0.3B", "cyber_readiness": 76,
        "geopolitical_summary": "Nuclear-armed South Asian power, home to the China-Pakistan Economic Corridor."
    },
    {
        "id": "BD", "iso3": "BGD", "name": "Bangladesh", "official_name": "Bangladesh",
        "flag": "BD", "capital": "Dhaka", "region": "Asia", "subregion": "Asia",
        "lat": 23.8103, "lon": 90.4125, "population": 171000000, "area_sq_km": 147570,
        "currency_code": "BDT", "currency_symbol": "\u09f3", "currency_name": "Bangladeshi Taka",
        "languages": ["Bengali"], "utc_offset": 6.0,
        "alliances": ["SAARC", "BIMSTEC"], "strategic_assets": ["Chittagong Port", "Garment Export Base", "Bay of Bengal Littoral"],
        "military_active": "160,000 Active", "defense_budget": ".2B", "cyber_readiness": 70,
        "geopolitical_summary": "World second-largest apparel exporter, strategic Bay of Bengal anchor."
    },
    {
        "id": "NZ", "iso3": "NZL", "name": "New Zealand", "official_name": "New Zealand",
        "flag": "NZ", "capital": "Wellington", "region": "Oceania", "subregion": "Oceania",
        "lat": -41.2865, "lon": 174.7762, "population": 5200000, "area_sq_km": 268021,
        "currency_code": "NZD", "currency_symbol": "NZ$", "currency_name": "New Zealand Dollar",
        "languages": ["English"], "utc_offset": 12.0,
        "alliances": ["Five Eyes", "CPTPP"], "strategic_assets": ["Rocket Lab Launch Pad (Mahia)", "Antarctic Gateway"],
        "military_active": "9,000 Active", "defense_budget": ".1B", "cyber_readiness": 86,
        "geopolitical_summary": "Five Eyes Pacific partner and commercial space launch pioneer."
    },
    {
        "id": "KZ", "iso3": "KAZ", "name": "Kazakhstan", "official_name": "Kazakhstan",
        "flag": "KZ", "capital": "Astana", "region": "Asia", "subregion": "Asia",
        "lat": 51.1694, "lon": 71.4491, "population": 20000000, "area_sq_km": 2724900,
        "currency_code": "KZT", "currency_symbol": "\u20b8", "currency_name": "Kazakhstani Tenge",
        "languages": ["Kazakh", "Russian"], "utc_offset": 5.0,
        "alliances": ["SCO", "CSTO"], "strategic_assets": ["Baikonur Cosmodrome", "Uranium Mines (40% World Total)", "Tengiz Oil"],
        "military_active": "45,000 Active", "defense_budget": ".5B", "cyber_readiness": 78,
        "geopolitical_summary": "Produces over 40% of the world uranium, largest economy in Central Asia."
    },
    {
        "id": "UZ", "iso3": "UZB", "name": "Uzbekistan", "official_name": "Uzbekistan",
        "flag": "UZ", "capital": "Tashkent", "region": "Asia", "subregion": "Asia",
        "lat": 41.2995, "lon": 69.2401, "population": 36000000, "area_sq_km": 447400,
        "currency_code": "UZS", "currency_symbol": "so\u02bbm", "currency_name": "Uzbekistani Som",
        "languages": ["Uzbek"], "utc_offset": 5.0,
        "alliances": ["SCO", "CIS"], "strategic_assets": ["Muruntau Gold Mine (World Largest Open Pit)", "Cotton Agronomy"],
        "military_active": "50,000 Active", "defense_budget": ".8B", "cyber_readiness": 68,
        "geopolitical_summary": "Most populous Central Asian nation, double-landlocked mineral and gold giant."
    },
    {
        "id": "SA", "iso3": "SAU", "name": "Saudi Arabia", "official_name": "Saudi Arabia",
        "flag": "SA", "capital": "Riyadh", "region": "Middle East", "subregion": "Middle East",
        "lat": 24.7136, "lon": 46.6753, "population": 36500000, "area_sq_km": 2149690,
        "currency_code": "SAR", "currency_symbol": "\ufdfc", "currency_name": "Saudi Riyal",
        "languages": ["Arabic"], "utc_offset": 3.0,
        "alliances": ["OPEC+", "BRICS+", "GCC", "G20"], "strategic_assets": ["Ghawar Oil Field", "Ras Tanura Terminal", "NEOM Corridor"],
        "military_active": "257,000 Active", "defense_budget": "1B", "cyber_readiness": 95,
        "geopolitical_summary": "De facto leader of OPEC and global hydrocarbon swing producer."
    },
    {
        "id": "AE", "iso3": "ARE", "name": "United Arab Emirates", "official_name": "United Arab Emirates",
        "flag": "AE", "capital": "Abu Dhabi", "region": "Middle East", "subregion": "Middle East",
        "lat": 24.4539, "lon": 54.3773, "population": 10200000, "area_sq_km": 83600,
        "currency_code": "AED", "currency_symbol": "\u062f.\u0625", "currency_name": "UAE Dirham",
        "languages": ["Arabic"], "utc_offset": 4.0,
        "alliances": ["OPEC+", "BRICS+", "GCC"], "strategic_assets": ["Jebel Ali Port", "Barakah Nuclear Plant", "Fujairah Crude Bypass"],
        "military_active": "63,000 Active", "defense_budget": "1B", "cyber_readiness": 94,
        "geopolitical_summary": "Financial and aviation crossroads, operates Hormuz crude bypass pipeline."
    },
    {
        "id": "IL", "iso3": "ISR", "name": "Israel", "official_name": "Israel",
        "flag": "IL", "capital": "Jerusalem / Tel Aviv", "region": "Middle East", "subregion": "Middle East",
        "lat": 31.7683, "lon": 35.2137, "population": 9800000, "area_sq_km": 22072,
        "currency_code": "ILS", "currency_symbol": "\u20aa", "currency_name": "Israeli New Shekel",
        "languages": ["Hebrew"], "utc_offset": 2.0,
        "alliances": ["Major Non-NATO Ally"], "strategic_assets": ["Unit 8200 Cyber", "Iron Dome Defense", "Leviathan Gas"],
        "military_active": "170,000 Active", "defense_budget": "4B", "cyber_readiness": 98,
        "geopolitical_summary": "Elite cyber, defense tech, and artificial intelligence developer."
    },
    {
        "id": "IR", "iso3": "IRN", "name": "Iran", "official_name": "Iran",
        "flag": "IR", "capital": "Tehran", "region": "Middle East", "subregion": "Middle East",
        "lat": 35.6892, "lon": 51.389, "population": 89000000, "area_sq_km": 1648195,
        "currency_code": "IRR", "currency_symbol": "\ufdfc", "currency_name": "Iranian Rial",
        "languages": ["Persian"], "utc_offset": 3.5,
        "alliances": ["BRICS+", "SCO"], "strategic_assets": ["Strait of Hormuz Missiles", "South Pars Gas", "Natanz"],
        "military_active": "610,000 Active", "defense_budget": "0B", "cyber_readiness": 88,
        "geopolitical_summary": "Dominates the northern coastline of the Strait of Hormuz, missile power."
    },
    {
        "id": "QA", "iso3": "QAT", "name": "Qatar", "official_name": "Qatar",
        "flag": "QA", "capital": "Doha", "region": "Middle East", "subregion": "Middle East",
        "lat": 25.2854, "lon": 51.531, "population": 3000000, "area_sq_km": 11586,
        "currency_code": "QAR", "currency_symbol": "\ufdfc", "currency_name": "Qatari Riyal",
        "languages": ["Arabic"], "utc_offset": 3.0,
        "alliances": ["GCC", "Major Non-NATO Ally"], "strategic_assets": ["North Field LNG Mega-Facilities", "Al Udeid Air Base"],
        "military_active": "16,500 Active", "defense_budget": ".0B", "cyber_readiness": 90,
        "geopolitical_summary": "World premier exporter of liquefied natural gas (LNG)."
    },
    {
        "id": "KW", "iso3": "KWT", "name": "Kuwait", "official_name": "Kuwait",
        "flag": "KW", "capital": "Kuwait City", "region": "Middle East", "subregion": "Middle East",
        "lat": 29.3759, "lon": 47.9774, "population": 4300000, "area_sq_km": 17818,
        "currency_code": "KWD", "currency_symbol": "KD", "currency_name": "Kuwaiti Dinar",
        "languages": ["Arabic"], "utc_offset": 3.0,
        "alliances": ["OPEC", "GCC"], "strategic_assets": ["Burgan Oil Field", "Kuwait Investment Authority (00B)"],
        "military_active": "17,500 Active", "defense_budget": ".2B", "cyber_readiness": 85,
        "geopolitical_summary": "Highest-valued currency unit in the world, massive sovereign wealth fund."
    },
    {
        "id": "OM", "iso3": "OMN", "name": "Oman", "official_name": "Oman",
        "flag": "OM", "capital": "Muscat", "region": "Middle East", "subregion": "Middle East",
        "lat": 23.5859, "lon": 58.4059, "population": 5100000, "area_sq_km": 309500,
        "currency_code": "OMR", "currency_symbol": "\ufdfc", "currency_name": "Omani Rial",
        "languages": ["Arabic"], "utc_offset": 4.0,
        "alliances": ["GCC"], "strategic_assets": ["Strait of Hormuz Musandam Sentinel", "Duqm Deepwater Port"],
        "military_active": "42,000 Active", "defense_budget": ".8B", "cyber_readiness": 82,
        "geopolitical_summary": "Controls the southern tip of the Strait of Hormuz, strategic diplomat of the Gulf."
    },
    {
        "id": "IQ", "iso3": "IRQ", "name": "Iraq", "official_name": "Iraq",
        "flag": "IQ", "capital": "Baghdad", "region": "Middle East", "subregion": "Middle East",
        "lat": 33.3152, "lon": 44.3661, "population": 45000000, "area_sq_km": 438317,
        "currency_code": "IQD", "currency_symbol": "\u0639.\u062f", "currency_name": "Iraqi Dinar",
        "languages": ["Arabic", "Kurdish"], "utc_offset": 3.0,
        "alliances": ["OPEC", "Arab League"], "strategic_assets": ["Rumaila Mega-Oilfield", "Al Faw Grand Port", "Basra Terminal"],
        "military_active": "200,000 Active", "defense_budget": ".5B", "cyber_readiness": 68,
        "geopolitical_summary": "Second-largest crude producer in OPEC, vital Euphrates-Tigris corridor."
    },
    {
        "id": "EG", "iso3": "EGY", "name": "Egypt", "official_name": "Egypt",
        "flag": "EG", "capital": "Cairo", "region": "Africa", "subregion": "Africa",
        "lat": 30.0444, "lon": 31.2357, "population": 105000000, "area_sq_km": 1002450,
        "currency_code": "EGP", "currency_symbol": "E\u00a3", "currency_name": "Egyptian Pound",
        "languages": ["Arabic"], "utc_offset": 2.0,
        "alliances": ["BRICS+", "Arab League", "AU"], "strategic_assets": ["Suez Canal Corridor", "Zohr Gas Field", "Aswan Dam"],
        "military_active": "438,000 Active", "defense_budget": ".1B", "cyber_readiness": 75,
        "geopolitical_summary": "Gatekeeper of the Suez Canal handling ~12% of world sea commerce."
    },
    {
        "id": "ZA", "iso3": "ZAF", "name": "South Africa", "official_name": "South Africa",
        "flag": "ZA", "capital": "Pretoria", "region": "Africa", "subregion": "Africa",
        "lat": -25.7479, "lon": 28.2293, "population": 60400000, "area_sq_km": 1221037,
        "currency_code": "ZAR", "currency_symbol": "R", "currency_name": "South African Rand",
        "languages": ["English", "Zulu", "Afrikaans"], "utc_offset": 2.0,
        "alliances": ["BRICS+", "G20", "AU"], "strategic_assets": ["Cape of Good Hope Route", "Platinum Mines", "Durban Port"],
        "military_active": "73,000 Active", "defense_budget": ".1B", "cyber_readiness": 79,
        "geopolitical_summary": "Industrial anchor of Sub-Saharan Africa, dominant platinum and chrome supplier."
    },
    {
        "id": "NG", "iso3": "NGA", "name": "Nigeria", "official_name": "Nigeria",
        "flag": "NG", "capital": "Abuja", "region": "Africa", "subregion": "Africa",
        "lat": 9.0765, "lon": 7.3986, "population": 224000000, "area_sq_km": 923768,
        "currency_code": "NGN", "currency_symbol": "\u20a6", "currency_name": "Nigerian Naira",
        "languages": ["English"], "utc_offset": 1.0,
        "alliances": ["OPEC", "ECOWAS", "AU"], "strategic_assets": ["Niger Delta Oil", "Dangote Refinery (650k bpd)", "Lekki Port"],
        "military_active": "143,000 Active", "defense_budget": ".2B", "cyber_readiness": 72,
        "geopolitical_summary": "Most populous African nation, crude producer with largest single-train refinery."
    },
    {
        "id": "KE", "iso3": "KEN", "name": "Kenya", "official_name": "Kenya",
        "flag": "KE", "capital": "Nairobi", "region": "Africa", "subregion": "Africa",
        "lat": -1.2921, "lon": 36.8219, "population": 55000000, "area_sq_km": 580367,
        "currency_code": "KES", "currency_symbol": "KSh", "currency_name": "Kenyan Shilling",
        "languages": ["Swahili", "English"], "utc_offset": 3.0,
        "alliances": ["EAC", "Major Non-NATO Ally"], "strategic_assets": ["Mombasa Deepwater Port", "Olkaria Geothermal Field"],
        "military_active": "24,000 Active", "defense_budget": ".4B", "cyber_readiness": 76,
        "geopolitical_summary": "Commercial and tech epicenter of East Africa, green energy champion."
    },
    {
        "id": "MA", "iso3": "MAR", "name": "Morocco", "official_name": "Morocco",
        "flag": "MA", "capital": "Rabat", "region": "Africa", "subregion": "Africa",
        "lat": 34.0209, "lon": -6.8416, "population": 37800000, "area_sq_km": 446550,
        "currency_code": "MAD", "currency_symbol": "DH", "currency_name": "Moroccan Dirham",
        "languages": ["Arabic", "Berber"], "utc_offset": 1.0,
        "alliances": ["Arab League", "Major Non-NATO Ally"], "strategic_assets": ["Tanger-Med Port", "OCP Phosphate Reserves (70% World Total)"],
        "military_active": "195,000 Active", "defense_budget": ".4B", "cyber_readiness": 78,
        "geopolitical_summary": "Controls over 70% of world phosphate reserves critical to food fertilizer."
    },
    {
        "id": "DZ", "iso3": "DZA", "name": "Algeria", "official_name": "Algeria",
        "flag": "DZ", "capital": "Algiers", "region": "Africa", "subregion": "Africa",
        "lat": 36.7538, "lon": 3.0588, "population": 45000000, "area_sq_km": 2381741,
        "currency_code": "DZD", "currency_symbol": "DA", "currency_name": "Algerian Dinar",
        "languages": ["Arabic", "Berber"], "utc_offset": 1.0,
        "alliances": ["OPEC", "AU"], "strategic_assets": ["Hassi Messaoud Oil Field", "Trans-Mediterranean Gas Pipelines"],
        "military_active": "312,000 Active", "defense_budget": "1.6B", "cyber_readiness": 75,
        "geopolitical_summary": "Largest territorial country in Africa, premier gas pipeline supplier to Southern Europe."
    },
    {
        "id": "ET", "iso3": "ETH", "name": "Ethiopia", "official_name": "Ethiopia",
        "flag": "ET", "capital": "Addis Ababa", "region": "Africa", "subregion": "Africa",
        "lat": 9.03, "lon": 38.74, "population": 126000000, "area_sq_km": 1104300,
        "currency_code": "ETB", "currency_symbol": "Br", "currency_name": "Ethiopian Birr",
        "languages": ["Amharic"], "utc_offset": 3.0,
        "alliances": ["BRICS+", "AU HQ"], "strategic_assets": ["Grand Ethiopian Renaissance Dam (GERD)", "Ethiopian Airlines Hub"],
        "military_active": "162,000 Active", "defense_budget": ".5B", "cyber_readiness": 67,
        "geopolitical_summary": "Second-most populous African country, home to African Union HQ and GERD dam."
    },
    {
        "id": "GH", "iso3": "GHA", "name": "Ghana", "official_name": "Ghana",
        "flag": "GH", "capital": "Accra", "region": "Africa", "subregion": "Africa",
        "lat": 5.6037, "lon": -0.187, "population": 34000000, "area_sq_km": 238533,
        "currency_code": "GHS", "currency_symbol": "GH\u20b5", "currency_name": "Ghanaian Cedi",
        "languages": ["English"], "utc_offset": 0.0,
        "alliances": ["ECOWAS", "AU"], "strategic_assets": ["Tema Port", "Gold & Cocoa Exports", "Offshore Jubilee Oil"],
        "military_active": "15,500 Active", "defense_budget": "80M", "cyber_readiness": 74,
        "geopolitical_summary": "Premier gold producer in Africa and stable West African democratic beacon."
    },
    {
        "id": "IS", "iso3": "ISL", "name": "Iceland", "official_name": "Iceland",
        "flag": "\ud83c\uddee\ud83c\uddf8", "capital": "Reykjavik", "region": "Europe", "subregion": "Europe",
        "lat": 64.1466, "lon": -21.9426, "population": 390000, "area_sq_km": 103000,
        "currency_code": "ISK", "currency_symbol": "kr", "currency_name": "Icelandic Krona",
        "languages": ["Icelandic"], "utc_offset": 0.0,
        "alliances": ["NATO", "EFTA"], "strategic_assets": ["Geothermal Energy", "Transatlantic Cable Gateway"],
        "military_active": "No Standing Military", "defense_budget": "0M", "cyber_readiness": 90,
        "geopolitical_summary": "Mid-Atlantic strategic island nation, 100% renewable energy."
    },
    {
        "id": "LU", "iso3": "LUX", "name": "Luxembourg", "official_name": "Luxembourg",
        "flag": "\ud83c\uddf1\ud83c\uddfa", "capital": "Luxembourg City", "region": "Europe", "subregion": "Europe",
        "lat": 49.6116, "lon": 6.1319, "population": 660000, "area_sq_km": 2586,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Luxembourgish", "French", "German"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["European Investment Bank", "SES Satellite Fleet"],
        "military_active": "1,000 Active", "defense_budget": "00M", "cyber_readiness": 91,
        "geopolitical_summary": "Global satellite telecommunications and private banking hub."
    },
    {
        "id": "HR", "iso3": "HRV", "name": "Croatia", "official_name": "Croatia",
        "flag": "\ud83c\udded\ud83c\uddf7", "capital": "Zagreb", "region": "Europe", "subregion": "Europe",
        "lat": 45.815, "lon": 15.9819, "population": 3900000, "area_sq_km": 56594,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Croatian"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Adriatic Seaports (Rijeka)", "LNG Terminal Krk"],
        "military_active": "15,000 Active", "defense_budget": ".4B", "cyber_readiness": 80,
        "geopolitical_summary": "Key Adriatic energy corridor with Krk LNG terminal supplying Central Europe."
    },
    {
        "id": "RS", "iso3": "SRB", "name": "Serbia", "official_name": "Serbia",
        "flag": "\ud83c\uddf7\ud83c\uddf8", "capital": "Belgrade", "region": "Europe", "subregion": "Europe",
        "lat": 44.7866, "lon": 20.4489, "population": 6600000, "area_sq_km": 88361,
        "currency_code": "RSD", "currency_symbol": "din.", "currency_name": "Serbian Dinar",
        "languages": ["Serbian"], "utc_offset": 1.0,
        "alliances": ["Non-Aligned"], "strategic_assets": ["Danube-Sava Crossroads", "Jadar Lithium Basin"],
        "military_active": "28,000 Active", "defense_budget": ".6B", "cyber_readiness": 76,
        "geopolitical_summary": "Major Balkan crossroads holding significant European lithium reserves."
    },
    {
        "id": "SK", "iso3": "SVK", "name": "Slovakia", "official_name": "Slovakia",
        "flag": "\ud83c\uddf8\ud83c\uddf0", "capital": "Bratislava", "region": "Europe", "subregion": "Europe",
        "lat": 48.1486, "lon": 17.1077, "population": 5400000, "area_sq_km": 49036,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Slovak"], "utc_offset": 1.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Automotive Capital of Europe", "Nuclear Plants"],
        "military_active": "19,000 Active", "defense_budget": ".6B", "cyber_readiness": 82,
        "geopolitical_summary": "World leading per-capita automobile producer and nuclear power operator."
    },
    {
        "id": "BG", "iso3": "BGR", "name": "Bulgaria", "official_name": "Bulgaria",
        "flag": "\ud83c\udde7\ud83c\uddec", "capital": "Sofia", "region": "Europe", "subregion": "Europe",
        "lat": 42.6977, "lon": 23.3219, "population": 6400000, "area_sq_km": 110994,
        "currency_code": "BGN", "currency_symbol": "\u043b\u0432", "currency_name": "Bulgarian Lev",
        "languages": ["Bulgarian"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Black Sea Naval Ports (Varna, Burgas)", "Balkan Gas"],
        "military_active": "37,000 Active", "defense_budget": ".8B", "cyber_readiness": 78,
        "geopolitical_summary": "Southern NATO Black Sea flank and regional gas transit crossroads."
    },
    {
        "id": "EE", "iso3": "EST", "name": "Estonia", "official_name": "Estonia",
        "flag": "\ud83c\uddea\ud83c\uddea", "capital": "Tallinn", "region": "Europe", "subregion": "Europe",
        "lat": 59.437, "lon": 24.7536, "population": 1360000, "area_sq_km": 45227,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Estonian"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["NATO Cooperative Cyber Defense Center (CCDCOE)", "e-Residency"],
        "military_active": "7,500 Active (230k Reserves)", "defense_budget": ".4B", "cyber_readiness": 98,
        "geopolitical_summary": "World foremost digital governance pioneer and host of NATO cyber defense headquarters."
    },
    {
        "id": "LV", "iso3": "LVA", "name": "Latvia", "official_name": "Latvia",
        "flag": "\ud83c\uddf1\ud83c\uddfb", "capital": "Riga", "region": "Europe", "subregion": "Europe",
        "lat": 56.9496, "lon": 24.1052, "population": 1880000, "area_sq_km": 64589,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Latvian"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Riga Transshipment Port", "NATO StratCom Center"],
        "military_active": "6,500 Active", "defense_budget": ".1B", "cyber_readiness": 85,
        "geopolitical_summary": "Baltic strategic pivot hosting NATO Strategic Communications Center of Excellence."
    },
    {
        "id": "LT", "iso3": "LTU", "name": "Lithuania", "official_name": "Lithuania",
        "flag": "\ud83c\uddf1\ud83c\uddf9", "capital": "Vilnius", "region": "Europe", "subregion": "Europe",
        "lat": 54.6872, "lon": 25.2797, "population": 2860000, "area_sq_km": 65300,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Lithuanian"], "utc_offset": 2.0,
        "alliances": ["EU", "NATO"], "strategic_assets": ["Klaipeda LNG Independence Terminal", "Suwalki Gap Border"],
        "military_active": "23,000 Active", "defense_budget": ".2B", "cyber_readiness": 88,
        "geopolitical_summary": "Guardian of the Suwalki Corridor connecting Poland and the Baltic states."
    },
    {
        "id": "CY", "iso3": "CYP", "name": "Cyprus", "official_name": "Cyprus",
        "flag": "\ud83c\udde8\ud83c\uddfe", "capital": "Nicosia", "region": "Europe", "subregion": "Europe",
        "lat": 35.1856, "lon": 33.3823, "population": 1250000, "area_sq_km": 9251,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Greek", "Turkish"], "utc_offset": 2.0,
        "alliances": ["EU"], "strategic_assets": ["RAF Akrotiri Sovereign Base", "Levantine Offshore Gas"],
        "military_active": "12,000 Active", "defense_budget": "50M", "cyber_readiness": 79,
        "geopolitical_summary": "Eastern Mediterranean unsinkable aircraft carrier commanding Levant approaches."
    },
    {
        "id": "MT", "iso3": "MLT", "name": "Malta", "official_name": "Malta",
        "flag": "\ud83c\uddf2\ud83c\uddf9", "capital": "Valletta", "region": "Europe", "subregion": "Europe",
        "lat": 35.8989, "lon": 14.5146, "population": 530000, "area_sq_km": 316,
        "currency_code": "EUR", "currency_symbol": "\u20ac", "currency_name": "Euro",
        "languages": ["Maltese", "English"], "utc_offset": 1.0,
        "alliances": ["EU", "Commonwealth"], "strategic_assets": ["Marsaxlokk Transshipment Freeport", "Maritime Flag Registry"],
        "military_active": "2,000 Active", "defense_budget": "10M", "cyber_readiness": 83,
        "geopolitical_summary": "Chokepoint island between Sicily and North Africa, major container transshipment hub."
    },
    {
        "id": "NP", "iso3": "NPL", "name": "Nepal", "official_name": "Nepal",
        "flag": "\ud83c\uddf3\ud83c\uddf5", "capital": "Kathmandu", "region": "Asia", "subregion": "Asia",
        "lat": 27.7172, "lon": 85.324, "population": 31000000, "area_sq_km": 147516,
        "currency_code": "NPR", "currency_symbol": "\u0930\u0942", "currency_name": "Nepalese Rupee",
        "languages": ["Nepali"], "utc_offset": 5.75,
        "alliances": ["SAARC"], "strategic_assets": ["Himalayan Water Towers", "Gurkha Tradition"],
        "military_active": "96,000 Active", "defense_budget": "80M", "cyber_readiness": 60,
        "geopolitical_summary": "Buffer state between India and China, major freshwater hydroelectric potential."
    },
    {
        "id": "LK", "iso3": "LKA", "name": "Sri Lanka", "official_name": "Sri Lanka",
        "flag": "\ud83c\uddf1\ud83c\uddf0", "capital": "Colombo", "region": "Asia", "subregion": "Asia",
        "lat": 6.9271, "lon": 79.8612, "population": 22200000, "area_sq_km": 65610,
        "currency_code": "LKR", "currency_symbol": "Rs", "currency_name": "Sri Lankan Rupee",
        "languages": ["Sinhala", "Tamil"], "utc_offset": 5.5,
        "alliances": ["SAARC", "BIMSTEC"], "strategic_assets": ["Hambantota Deep Seaport", "Colombo Transshipment Hub"],
        "military_active": "250,000 Active", "defense_budget": ".8B", "cyber_readiness": 72,
        "geopolitical_summary": "Controls central Indian Ocean East-West international shipping routes."
    },
    {
        "id": "MM", "iso3": "MMR", "name": "Myanmar", "official_name": "Myanmar",
        "flag": "\ud83c\uddf2\ud83c\uddf2", "capital": "Naypyidaw", "region": "Asia", "subregion": "Asia",
        "lat": 19.7633, "lon": 96.0785, "population": 54000000, "area_sq_km": 676578,
        "currency_code": "MMK", "currency_symbol": "K", "currency_name": "Myanmar Kyat",
        "languages": ["Burmese"], "utc_offset": 6.5,
        "alliances": ["ASEAN"], "strategic_assets": ["Kyaukpyu Deepwater Port", "Natural Gas Pipelines"],
        "military_active": "350,000 Active", "defense_budget": ".2B", "cyber_readiness": 50,
        "geopolitical_summary": "Strategic Indian Ocean littoral providing direct overland corridor from Yunnan."
    },
    {
        "id": "KH", "iso3": "KHM", "name": "Cambodia", "official_name": "Cambodia",
        "flag": "\ud83c\uddf0\ud83c\udded", "capital": "Phnom Penh", "region": "Asia", "subregion": "Asia",
        "lat": 11.5564, "lon": 104.9282, "population": 16800000, "area_sq_km": 181035,
        "currency_code": "KHR", "currency_symbol": "\u17db", "currency_name": "Cambodian Riel",
        "languages": ["Khmer"], "utc_offset": 7.0,
        "alliances": ["ASEAN"], "strategic_assets": ["Ream Naval Base (Gulf of Thailand)", "Mekong Basin"],
        "military_active": "125,000 Active", "defense_budget": "50M", "cyber_readiness": 58,
        "geopolitical_summary": "Gulf of Thailand coastal state developing major deepwater naval infrastructure."
    },
    {
        "id": "MN", "iso3": "MNG", "name": "Mongolia", "official_name": "Mongolia",
        "flag": "\ud83c\uddf2\ud83c\uddf3", "capital": "Ulaanbaatar", "region": "Asia", "subregion": "Asia",
        "lat": 47.8864, "lon": 106.9057, "population": 3400000, "area_sq_km": 1564116,
        "currency_code": "MNT", "currency_symbol": "\u20ae", "currency_name": "Mongolian Tugrik",
        "languages": ["Mongolian"], "utc_offset": 8.0,
        "alliances": ["Third Neighbor Policy"], "strategic_assets": ["Oyu Tolgoi Copper-Gold Mine", "Tavan Tolgoi Coal"],
        "military_active": "10,000 Active", "defense_budget": "40M", "cyber_readiness": 65,
        "geopolitical_summary": "Vast mineral-rich buffer state balancing China and Russia."
    },
    {
        "id": "JO", "iso3": "JOR", "name": "Jordan", "official_name": "Jordan",
        "flag": "\ud83c\uddef\ud83c\uddf4", "capital": "Amman", "region": "Middle East", "subregion": "Middle East",
        "lat": 31.9454, "lon": 35.9284, "population": 11300000, "area_sq_km": 89342,
        "currency_code": "JOD", "currency_symbol": "JD", "currency_name": "Jordanian Dinar",
        "languages": ["Arabic"], "utc_offset": 3.0,
        "alliances": ["Major Non-NATO Ally"], "strategic_assets": ["Aqaba Red Sea Port", "Muwaffaq Salti Air Base"],
        "military_active": "100,000 Active", "defense_budget": ".1B", "cyber_readiness": 78,
        "geopolitical_summary": "Anchor of regional stability bordering Israel, Syria, Iraq, and Saudi Arabia."
    },
    {
        "id": "BH", "iso3": "BHR", "name": "Bahrain", "official_name": "Bahrain",
        "flag": "\ud83c\udde7\ud83c\udded", "capital": "Manama", "region": "Middle East", "subregion": "Middle East",
        "lat": 26.2285, "lon": 50.586, "population": 1500000, "area_sq_km": 786,
        "currency_code": "BHD", "currency_symbol": "BD", "currency_name": "Bahraini Dinar",
        "languages": ["Arabic"], "utc_offset": 3.0,
        "alliances": ["Major Non-NATO Ally", "GCC"], "strategic_assets": ["US Navy 5th Fleet Headquarters", "BAPCO Refinery"],
        "military_active": "8,200 Active", "defense_budget": ".5B", "cyber_readiness": 86,
        "geopolitical_summary": "Hosts the operational headquarters for all US naval forces in the Middle East."
    },
    {
        "id": "UG", "iso3": "UGA", "name": "Uganda", "official_name": "Uganda",
        "flag": "\ud83c\uddfa\ud83c\uddec", "capital": "Kampala", "region": "Africa", "subregion": "Africa",
        "lat": 0.3476, "lon": 32.5825, "population": 48000000, "area_sq_km": 241038,
        "currency_code": "UGX", "currency_symbol": "USh", "currency_name": "Ugandan Shilling",
        "languages": ["English", "Swahili"], "utc_offset": 3.0,
        "alliances": ["EAC", "AU"], "strategic_assets": ["Lake Victoria Basin", "Lake Albert Crude (EACOP)"],
        "military_active": "45,000 Active", "defense_budget": ".0B", "cyber_readiness": 68,
        "geopolitical_summary": "Great Lakes security anchor, developing East African Crude Oil Pipeline."
    },
    {
        "id": "TZ", "iso3": "TZA", "name": "Tanzania", "official_name": "Tanzania",
        "flag": "\ud83c\uddf9\ud83c\uddff", "capital": "Dodoma / Dar es Salaam", "region": "Africa", "subregion": "Africa",
        "lat": -6.163, "lon": 35.7516, "population": 67000000, "area_sq_km": 947303,
        "currency_code": "TZS", "currency_symbol": "TSh", "currency_name": "Tanzanian Shilling",
        "languages": ["Swahili", "English"], "utc_offset": 3.0,
        "alliances": ["EAC", "SADC"], "strategic_assets": ["Dar es Salaam Seaport", "Offshore Deep Gas Basins"],
        "military_active": "27,000 Active", "defense_budget": "50M", "cyber_readiness": 70,
        "geopolitical_summary": "Indian Ocean maritime gateway for 6 landlocked East/Central African states."
    },
    {
        "id": "AO", "iso3": "AGO", "name": "Angola", "official_name": "Angola",
        "flag": "\ud83c\udde6\ud83c\uddf4", "capital": "Luanda", "region": "Africa", "subregion": "Africa",
        "lat": -8.839, "lon": 13.2894, "population": 36000000, "area_sq_km": 1246700,
        "currency_code": "AOA", "currency_symbol": "Kz", "currency_name": "Angolan Kwanza",
        "languages": ["Portuguese"], "utc_offset": 1.0,
        "alliances": ["OPEC (Former)", "AU"], "strategic_assets": ["Cabinda Deepwater Crude", "Lobito Rail Corridor"],
        "military_active": "107,000 Active", "defense_budget": ".8B", "cyber_readiness": 65,
        "geopolitical_summary": "Second-largest crude exporter in Sub-Saharan Africa, anchor of the Lobito Corridor."
    },
    {
        "id": "CI", "iso3": "CIV", "name": "Ivory Coast", "official_name": "Ivory Coast",
        "flag": "\ud83c\udde8\ud83c\uddee", "capital": "Yamoussoukro / Abidjan", "region": "Africa", "subregion": "Africa",
        "lat": 6.8276, "lon": -5.2893, "population": 30000000, "area_sq_km": 322463,
        "currency_code": "XOF", "currency_symbol": "CFA", "currency_name": "West African CFA Franc",
        "languages": ["French"], "utc_offset": 0.0,
        "alliances": ["ECOWAS", "AU"], "strategic_assets": ["Port of Abidjan (West Africa Hub)", "Cocoa Monopoly (45% World)"],
        "military_active": "25,000 Active", "defense_budget": "50M", "cyber_readiness": 74,
        "geopolitical_summary": "Economic engine of Francophone West Africa, world largest cocoa producer."
    },
    {
        "id": "CD", "iso3": "COD", "name": "DR Congo", "official_name": "DR Congo",
        "flag": "\ud83c\udde8\ud83c\udde9", "capital": "Kinshasa", "region": "Africa", "subregion": "Africa",
        "lat": -4.4419, "lon": 15.2663, "population": 102000000, "area_sq_km": 2344858,
        "currency_code": "CDF", "currency_symbol": "FC", "currency_name": "Congolese Franc",
        "languages": ["French", "Lingala"], "utc_offset": 1.0,
        "alliances": ["SADC", "EAC", "AU"], "strategic_assets": ["Katanga Cobalt Belt (70% World Total)", "Inga Hydro Dam"],
        "military_active": "134,000 Active", "defense_budget": "50M", "cyber_readiness": 45,
        "geopolitical_summary": "Supplies over 70% of the world cobalt and massive copper and coltan deposits."
    },
    {
        "id": "SN", "iso3": "SEN", "name": "Senegal", "official_name": "Senegal",
        "flag": "\ud83c\uddf8\ud83c\uddf3", "capital": "Dakar", "region": "Africa", "subregion": "Africa",
        "lat": 14.7167, "lon": -17.4677, "population": 18000000, "area_sq_km": 196722,
        "currency_code": "XOF", "currency_symbol": "CFA", "currency_name": "West African CFA Franc",
        "languages": ["French", "Wolof"], "utc_offset": 0.0,
        "alliances": ["ECOWAS", "AU"], "strategic_assets": ["Port of Dakar", "Sangomar Offshore Oil & GTA LNG"],
        "military_active": "17,000 Active", "defense_budget": "20M", "cyber_readiness": 76,
        "geopolitical_summary": "Democratic West African lighthouse with major new offshore oil and gas production."
    },
]
