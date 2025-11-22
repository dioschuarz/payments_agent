"""Comprehensive country data for validation and entity extraction.

This module provides a single source of truth for country mappings
used by both validators and AI prompts.
"""

# ISO 3166-1 alpha-2 country codes with common name variations
# Format: {name_variation: (code, official_name)}
COUNTRY_MAPPINGS = {
    # North America
    "usa": ("US", "United States"),
    "united states": ("US", "United States"),
    "united states of america": ("US", "United States"),
    "america": ("US", "United States"),
    "canada": ("CA", "Canada"),
    "mexico": ("MX", "Mexico"),
    "guatemala": ("GT", "Guatemala"),
    "belize": ("BZ", "Belize"),
    "el salvador": ("SV", "El Salvador"),
    "honduras": ("HN", "Honduras"),
    "nicaragua": ("NI", "Nicaragua"),
    "costa rica": ("CR", "Costa Rica"),
    "panama": ("PA", "Panama"),
    "cuba": ("CU", "Cuba"),
    "jamaica": ("JM", "Jamaica"),
    "haiti": ("HT", "Haiti"),
    "dominican republic": ("DO", "Dominican Republic"),
    "puerto rico": ("PR", "Puerto Rico"),
    "trinidad and tobago": ("TT", "Trinidad and Tobago"),
    "barbados": ("BB", "Barbados"),
    
    # South America
    "brazil": ("BR", "Brazil"),
    "argentina": ("AR", "Argentina"),
    "chile": ("CL", "Chile"),
    "colombia": ("CO", "Colombia"),
    "peru": ("PE", "Peru"),
    "venezuela": ("VE", "Venezuela"),
    "ecuador": ("EC", "Ecuador"),
    "bolivia": ("BO", "Bolivia"),
    "paraguay": ("PY", "Paraguay"),
    "uruguay": ("UY", "Uruguay"),
    "guyana": ("GY", "Guyana"),
    "suriname": ("SR", "Suriname"),
    "french guiana": ("GF", "French Guiana"),
    
    # Europe
    "united kingdom": ("GB", "United Kingdom"),
    "uk": ("GB", "United Kingdom"),
    "britain": ("GB", "United Kingdom"),
    "great britain": ("GB", "United Kingdom"),
    "spain": ("ES", "Spain"),
    "france": ("FR", "France"),
    "germany": ("DE", "Germany"),
    "italy": ("IT", "Italy"),
    "portugal": ("PT", "Portugal"),
    "netherlands": ("NL", "Netherlands"),
    "holland": ("NL", "Netherlands"),
    "belgium": ("BE", "Belgium"),
    "switzerland": ("CH", "Switzerland"),
    "austria": ("AT", "Austria"),
    "sweden": ("SE", "Sweden"),
    "norway": ("NO", "Norway"),
    "denmark": ("DK", "Denmark"),
    "finland": ("FI", "Finland"),
    "poland": ("PL", "Poland"),
    "greece": ("GR", "Greece"),
    "ireland": ("IE", "Ireland"),
    "russia": ("RU", "Russia"),
    "russian federation": ("RU", "Russia"),
    "ukraine": ("UA", "Ukraine"),
    "romania": ("RO", "Romania"),
    "hungary": ("HU", "Hungary"),
    "czech republic": ("CZ", "Czech Republic"),
    "czechia": ("CZ", "Czech Republic"),
    "slovakia": ("SK", "Slovakia"),
    "croatia": ("HR", "Croatia"),
    "serbia": ("RS", "Serbia"),
    "bulgaria": ("BG", "Bulgaria"),
    "slovenia": ("SI", "Slovenia"),
    "lithuania": ("LT", "Lithuania"),
    "latvia": ("LV", "Latvia"),
    "estonia": ("EE", "Estonia"),
    "iceland": ("IS", "Iceland"),
    "luxembourg": ("LU", "Luxembourg"),
    "malta": ("MT", "Malta"),
    "cyprus": ("CY", "Cyprus"),
    
    # Asia
    "japan": ("JP", "Japan"),
    "china": ("CN", "China"),
    "peoples republic of china": ("CN", "China"),
    "india": ("IN", "India"),
    "south korea": ("KR", "South Korea"),
    "korea": ("KR", "South Korea"),
    "north korea": ("KP", "North Korea"),
    "singapore": ("SG", "Singapore"),
    "malaysia": ("MY", "Malaysia"),
    "thailand": ("TH", "Thailand"),
    "indonesia": ("ID", "Indonesia"),
    "philippines": ("PH", "Philippines"),
    "vietnam": ("VN", "Vietnam"),
    "pakistan": ("PK", "Pakistan"),
    "bangladesh": ("BD", "Bangladesh"),
    "sri lanka": ("LK", "Sri Lanka"),
    "turkey": ("TR", "Turkey"),
    "saudi arabia": ("SA", "Saudi Arabia"),
    "united arab emirates": ("AE", "United Arab Emirates"),
    "uae": ("AE", "United Arab Emirates"),
    "israel": ("IL", "Israel"),
    "iran": ("IR", "Iran"),
    "iraq": ("IQ", "Iraq"),
    "afghanistan": ("AF", "Afghanistan"),
    "kazakhstan": ("KZ", "Kazakhstan"),
    "uzbekistan": ("UZ", "Uzbekistan"),
    "nepal": ("NP", "Nepal"),
    "myanmar": ("MM", "Myanmar"),
    "burma": ("MM", "Myanmar"),
    "cambodia": ("KH", "Cambodia"),
    "laos": ("LA", "Laos"),
    "mongolia": ("MN", "Mongolia"),
    "taiwan": ("TW", "Taiwan"),
    "hong kong": ("HK", "Hong Kong"),
    "macau": ("MO", "Macau"),
    "qatar": ("QA", "Qatar"),
    "kuwait": ("KW", "Kuwait"),
    "bahrain": ("BH", "Bahrain"),
    "oman": ("OM", "Oman"),
    "yemen": ("YE", "Yemen"),
    "jordan": ("JO", "Jordan"),
    "lebanon": ("LB", "Lebanon"),
    "syria": ("SY", "Syria"),
    
    # Africa
    "nigeria": ("NG", "Nigeria"),
    "south africa": ("ZA", "South Africa"),
    "egypt": ("EG", "Egypt"),
    "kenya": ("KE", "Kenya"),
    "ghana": ("GH", "Ghana"),
    "ethiopia": ("ET", "Ethiopia"),
    "tanzania": ("TZ", "Tanzania"),
    "uganda": ("UG", "Uganda"),
    "morocco": ("MA", "Morocco"),
    "algeria": ("DZ", "Algeria"),
    "tunisia": ("TN", "Tunisia"),
    "senegal": ("SN", "Senegal"),
    "ivory coast": ("CI", "Ivory Coast"),
    "cote divoire": ("CI", "Ivory Coast"),
    "cameroon": ("CM", "Cameroon"),
    "angola": ("AO", "Angola"),
    "mozambique": ("MZ", "Mozambique"),
    "madagascar": ("MG", "Madagascar"),
    "zimbabwe": ("ZW", "Zimbabwe"),
    "zambia": ("ZM", "Zambia"),
    "malawi": ("MW", "Malawi"),
    "zimbabwe": ("ZW", "Zimbabwe"),
    "botswana": ("BW", "Botswana"),
    "namibia": ("NA", "Namibia"),
    "rwanda": ("RW", "Rwanda"),
    "burundi": ("BI", "Burundi"),
    "somalia": ("SO", "Somalia"),
    "sudan": ("SD", "Sudan"),
    "south sudan": ("SS", "South Sudan"),
    "chad": ("TD", "Chad"),
    "niger": ("NE", "Niger"),
    "mali": ("ML", "Mali"),
    "burkina faso": ("BF", "Burkina Faso"),
    "guinea": ("GN", "Guinea"),
    "sierra leone": ("SL", "Sierra Leone"),
    "liberia": ("LR", "Liberia"),
    "gambia": ("GM", "Gambia"),
    "guinea bissau": ("GW", "Guinea-Bissau"),
    "cape verde": ("CV", "Cape Verde"),
    "mauritania": ("MR", "Mauritania"),
    "libya": ("LY", "Libya"),
    "eritrea": ("ER", "Eritrea"),
    "djibouti": ("DJ", "Djibouti"),
    "gabon": ("GA", "Gabon"),
    "equatorial guinea": ("GQ", "Equatorial Guinea"),
    "sao tome and principe": ("ST", "São Tomé and Príncipe"),
    "congo": ("CG", "Congo"),
    "democratic republic of the congo": ("CD", "Democratic Republic of the Congo"),
    "drc": ("CD", "Democratic Republic of the Congo"),
    "central african republic": ("CF", "Central African Republic"),
    "benin": ("BJ", "Benin"),
    "togo": ("TG", "Togo"),
    "mauritius": ("MU", "Mauritius"),
    "seychelles": ("SC", "Seychelles"),
    "comoros": ("KM", "Comoros"),
    "lesotho": ("LS", "Lesotho"),
    "eswatini": ("SZ", "Eswatini"),
    "swaziland": ("SZ", "Eswatini"),
    
    # Oceania
    "australia": ("AU", "Australia"),
    "new zealand": ("NZ", "New Zealand"),
    "papua new guinea": ("PG", "Papua New Guinea"),
    "fiji": ("FJ", "Fiji"),
    "samoa": ("WS", "Samoa"),
    "tonga": ("TO", "Tonga"),
    "vanuatu": ("VU", "Vanuatu"),
    "solomon islands": ("SB", "Solomon Islands"),
    "micronesia": ("FM", "Micronesia"),
    "palau": ("PW", "Palau"),
    "marshall islands": ("MH", "Marshall Islands"),
    "kiribati": ("KI", "Kiribati"),
    "nauru": ("NR", "Nauru"),
    "tuvalu": ("TV", "Tuvalu"),
}

# Reverse mapping: code -> official name
CODE_TO_NAME = {code: name for name, (code, _) in COUNTRY_MAPPINGS.items() if name not in ["uk", "usa", "america", "holland", "korea", "burma", "swaziland", "drc"]}
# Add direct code mappings
for (code, name) in set(COUNTRY_MAPPINGS.values()):
    CODE_TO_NAME[code] = name

def get_country_code(name: str) -> tuple[str, str] | None:
    """Get country code and official name from name variation."""
    name_lower = name.lower().strip()
    result = COUNTRY_MAPPINGS.get(name_lower)
    if result:
        return result
    return None

def get_country_name(code: str) -> str | None:
    """Get official country name from ISO code."""
    return CODE_TO_NAME.get(code.upper())

def get_all_country_names() -> list[str]:
    """Get list of all country names for prompts."""
    # Return unique official names
    return sorted(set(name for _, name in COUNTRY_MAPPINGS.values()))

def get_country_list_for_prompt() -> str:
    """Get formatted country list for AI prompts."""
    countries = get_all_country_names()
    # Return a comprehensive but concise list for prompts
    # Show first 30 countries as examples
    sample = ", ".join(countries[:30])
    remaining = len(countries) - 30
    return f"{sample} (and {remaining} more countries including all ISO 3166-1 countries)"

