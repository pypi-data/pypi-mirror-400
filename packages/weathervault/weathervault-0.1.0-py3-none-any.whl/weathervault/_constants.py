"""Constants for weathervault package."""

# Base URL for NCEI NOAA data
BASE_URL = "https://www.ncei.noaa.gov/pub/data/noaa"

# Column widths for the fixed-width mandatory data section
# Based on ISD format document
MANDATORY_COLUMN_WIDTHS = [
    4,  # Variable length indicator (total variable length)
    6,  # USAF station ID
    5,  # WBAN station ID
    4,  # Year
    2,  # Month
    2,  # Day
    2,  # Hour
    2,  # Minute
    1,  # Data source flag
    6,  # Latitude (scaled)
    7,  # Longitude (scaled)
    5,  # Report type code
    5,  # Elevation (scaled)
    5,  # Call letter identifier
    4,  # Quality control process name
    3,  # Wind direction angle
    1,  # Wind direction quality code
    1,  # Wind type code
    4,  # Wind speed rate (scaled)
    1,  # Wind speed quality code
    5,  # Ceiling height (scaled)
    1,  # Ceiling height quality code
    1,  # Ceiling determination code
    1,  # CAVOK code
    6,  # Visibility distance (scaled)
    1,  # Visibility distance quality code
    1,  # Visibility variability code
    1,  # Visibility variability quality code
    5,  # Air temperature (scaled)
    1,  # Air temperature quality code
    5,  # Dew point temperature (scaled)
    1,  # Dew point quality code
    5,  # Sea level pressure (scaled)
    1,  # Sea level pressure quality code
]

# Column names for the mandatory section
MANDATORY_COLUMN_NAMES = [
    "total_chars",
    "usaf",
    "wban",
    "year",
    "month",
    "day",
    "hour",
    "minute",
    "data_source",
    "latitude",
    "longitude",
    "report_type",
    "elevation",
    "call_letters",
    "qc_process",
    "wind_direction",
    "wind_direction_qc",
    "wind_type",
    "wind_speed",
    "wind_speed_qc",
    "ceiling_height",
    "ceiling_height_qc",
    "ceiling_determination",
    "cavok",
    "visibility",
    "visibility_qc",
    "visibility_variability",
    "visibility_variability_qc",
    "temp",
    "temp_qc",
    "dew_point",
    "dew_point_qc",
    "sea_level_pressure",
    "sea_level_pressure_qc",
]

# Missing value codes in ISD data
# Reference: NOAA ISD Format Document
# https://www.ncei.noaa.gov/data/global-hourly/doc/isd-format-document.pdf
MISSING_VALUES = {
    "wind_direction": 999,  # POS 61-63: 999 = Missing
    "wind_speed": 9999,  # POS 66-69: 9999 = Missing
    "ceiling_height": 99999,  # POS 71-75: 99999 = Missing
    "visibility": 999999,  # POS 79-84: 999999 = Missing
    "temp": 9999,  # POS 88-92: +9999 = Missing (stored without sign)
    "dew_point": 9999,  # POS 94-98: +9999 = Missing (stored without sign)
    "sea_level_pressure": 99999,  # POS 100-104: 99999 = Missing
}

# Scale factors for numeric fields (divide by this to get actual value)
SCALE_FACTORS = {
    "wind_speed": 10,  # m/s with 1 decimal
    "temp": 10,  # degrees C with 1 decimal
    "dew_point": 10,  # degrees C with 1 decimal
    "sea_level_pressure": 10,  # hectopascals with 1 decimal
    "latitude": 1000,  # degrees with 3 decimals
    "longitude": 1000,  # degrees with 3 decimals
    "elevation": 1,  # meters (already in meters)
}

# FIPS country codes to country names mapping
# From https://www.ncei.noaa.gov/pub/data/noaa/country-list.txt
COUNTRY_CODES = {
    "AA": "Aruba",
    "AC": "Antigua and Barbuda",
    "AF": "Afghanistan",
    "AG": "Algeria",
    "AI": "Ascension Island",
    "AJ": "Azerbaijan",
    "AL": "Albania",
    "AM": "Armenia",
    "AN": "Andorra",
    "AO": "Angola",
    "AQ": "American Samoa",
    "AR": "Argentina",
    "AS": "Australia",
    "AT": "Ashmore and Cartier Islands",
    "AU": "Austria",
    "AV": "Anguilla",
    "AY": "Antarctica",
    "AZ": "Azores",
    "BA": "Bahrain",
    "BB": "Barbados",
    "BC": "Botswana",
    "BD": "Bermuda",
    "BE": "Belgium",
    "BF": "Bahamas",
    "BG": "Bangladesh",
    "BH": "Belize",
    "BK": "Bosnia and Herzegovina",
    "BL": "Bolivia",
    "BM": "Burma",
    "BN": "Benin",
    "BO": "Belarus",
    "BP": "Solomon Islands",
    "BR": "Brazil",
    "BT": "Bhutan",
    "BU": "Bulgaria",
    "BV": "Bouvet Island",
    "BX": "Brunei",
    "BY": "Burundi",
    "CA": "Canada",
    "CB": "Cambodia",
    "CD": "Chad",
    "CE": "Sri Lanka",
    "CF": "Congo",
    "CG": "Zaire",
    "CH": "China",
    "CI": "Chile",
    "CJ": "Cayman Islands",
    "CK": "Cocos (Keeling) Islands",
    "CM": "Cameroon",
    "CN": "Comoros",
    "CO": "Colombia",
    "CQ": "Northern Mariana Islands",
    "CR": "Coral Sea Islands",
    "CS": "Costa Rica",
    "CT": "Central African Republic",
    "CU": "Cuba",
    "CV": "Cape Verde",
    "CW": "Cook Islands",
    "CY": "Cyprus",
    "DA": "Denmark",
    "DJ": "Djibouti",
    "DO": "Dominica",
    "DR": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "EI": "Ireland",
    "EK": "Equatorial Guinea",
    "EN": "Estonia",
    "ER": "Eritrea",
    "ES": "El Salvador",
    "ET": "Ethiopia",
    "EZ": "Czech Republic",
    "FG": "French Guiana",
    "FI": "Finland",
    "FJ": "Fiji",
    "FK": "Falkland Islands",
    "FM": "Micronesia",
    "FO": "Faroe Islands",
    "FP": "French Polynesia",
    "FR": "France",
    "GA": "Gambia",
    "GB": "Gabon",
    "GG": "Georgia",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GJ": "Grenada",
    "GK": "Guernsey",
    "GL": "Greenland",
    "GM": "Germany",
    "GP": "Guadeloupe",
    "GQ": "Guam",
    "GR": "Greece",
    "GT": "Guatemala",
    "GV": "Guinea",
    "GY": "Guyana",
    "GZ": "Gaza Strip",
    "HA": "Haiti",
    "HK": "Hong Kong",
    "HO": "Honduras",
    "HR": "Croatia",
    "HU": "Hungary",
    "IC": "Iceland",
    "ID": "Indonesia",
    "IM": "Isle of Man",
    "IN": "India",
    "IO": "British Indian Ocean Territory",
    "IR": "Iran",
    "IS": "Israel",
    "IT": "Italy",
    "IV": "Cote d'Ivoire",
    "IZ": "Iraq",
    "JA": "Japan",
    "JE": "Jersey",
    "JM": "Jamaica",
    "JN": "Jan Mayen",
    "JO": "Jordan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KN": "North Korea",
    "KR": "Kiribati",
    "KS": "South Korea",
    "KT": "Christmas Island",
    "KU": "Kuwait",
    "KV": "Kosovo",
    "KZ": "Kazakhstan",
    "LA": "Laos",
    "LE": "Lebanon",
    "LG": "Latvia",
    "LH": "Lithuania",
    "LI": "Liberia",
    "LO": "Slovakia",
    "LS": "Liechtenstein",
    "LT": "Lesotho",
    "LU": "Luxembourg",
    "LY": "Libya",
    "MA": "Madagascar",
    "MB": "Martinique",
    "MC": "Macau",
    "MD": "Moldova",
    "MF": "Mayotte",
    "MG": "Mongolia",
    "MH": "Montserrat",
    "MI": "Malawi",
    "MJ": "Montenegro",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MM": "Burma (Myanmar)",
    "MN": "Monaco",
    "MO": "Morocco",
    "MP": "Mauritius",
    "MR": "Mauritania",
    "MT": "Malta",
    "MU": "Oman",
    "MV": "Maldives",
    "MX": "Mexico",
    "MY": "Malaysia",
    "MZ": "Mozambique",
    "NC": "New Caledonia",
    "NE": "Niue",
    "NF": "Norfolk Island",
    "NG": "Niger",
    "NH": "Vanuatu",
    "NI": "Nigeria",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NS": "Suriname",
    "NU": "Nicaragua",
    "NZ": "New Zealand",
    "OD": "South Sudan",
    "PA": "Paraguay",
    "PC": "Pitcairn Islands",
    "PE": "Peru",
    "PG": "Spratly Islands",
    "PK": "Pakistan",
    "PL": "Poland",
    "PM": "Panama",
    "PO": "Portugal",
    "PP": "Papua New Guinea",
    "PS": "Palau",
    "PU": "Guinea-Bissau",
    "QA": "Qatar",
    "RE": "Reunion",
    "RI": "Serbia",
    "RM": "Marshall Islands",
    "RO": "Romania",
    "RP": "Philippines",
    "RQ": "Puerto Rico",
    "RS": "Russia",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SB": "St. Pierre and Miquelon",
    "SC": "St. Kitts and Nevis",
    "SE": "Seychelles",
    "SF": "South Africa",
    "SG": "Senegal",
    "SH": "St. Helena",
    "SI": "Slovenia",
    "SL": "Sierra Leone",
    "SM": "San Marino",
    "SN": "Singapore",
    "SO": "Somalia",
    "SP": "Spain",
    "SR": "Serbia",
    "ST": "St. Lucia",
    "SU": "Sudan",
    "SV": "Svalbard",
    "SW": "Sweden",
    "SX": "South Georgia",
    "SY": "Syria",
    "SZ": "Switzerland",
    "TC": "United Arab Emirates",
    "TD": "Trinidad and Tobago",
    "TH": "Thailand",
    "TI": "Tajikistan",
    "TK": "Turks and Caicos Islands",
    "TL": "Tokelau",
    "TN": "Tonga",
    "TO": "Togo",
    "TP": "Sao Tome and Principe",
    "TS": "Tunisia",
    "TU": "Turkey",
    "TV": "Tuvalu",
    "TW": "Taiwan",
    "TX": "Turkmenistan",
    "TZ": "Tanzania",
    "UG": "Uganda",
    "UK": "United Kingdom",
    "UP": "Ukraine",
    "US": "United States",
    "UV": "Burkina Faso",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VC": "St. Vincent and the Grenadines",
    "VE": "Venezuela",
    "VI": "Virgin Islands (British)",
    "VM": "Vietnam",
    "VQ": "Virgin Islands (U.S.)",
    "VT": "Vatican City",
    "WA": "Namibia",
    "WE": "West Bank",
    "WF": "Wallis and Futuna",
    "WI": "Western Sahara",
    "WQ": "Wake Island",
    "WS": "Western Samoa",
    "WZ": "Eswatini",
    "YM": "Yemen",
    "ZA": "Zambia",
    "ZI": "Zimbabwe",
    "ZM": "Samoa",
}

# FIPS to ISO 3166-1 alpha-2 country code mapping
# Maps the FIPS codes used in ISD data to standard ISO country codes
# This allows users to access stations using familiar ISO codes (e.g., DE for Germany)
# while internally working with the FIPS codes in the data
FIPS_TO_ISO = {
    "AA": "AW",  # Aruba
    "AC": "AG",  # Antigua and Barbuda
    "AF": "AF",  # Afghanistan (same)
    "AG": "DZ",  # Algeria
    "AI": "AC",  # Ascension Island (unofficial)
    "AJ": "AZ",  # Azerbaijan
    "AL": "AL",  # Albania (same)
    "AM": "AM",  # Armenia (same)
    "AN": "AD",  # Andorra
    "AO": "AO",  # Angola (same)
    "AQ": "AS",  # American Samoa
    "AR": "AR",  # Argentina (same)
    "AS": "AU",  # Australia
    "AT": "AU",  # Ashmore and Cartier Islands (part of Australia)
    "AU": "AT",  # Austria
    "AV": "AI",  # Anguilla
    "AY": "AQ",  # Antarctica
    "AZ": "PT",  # Azores (part of Portugal)
    "BA": "BH",  # Bahrain
    "BB": "BB",  # Barbados (same)
    "BC": "BW",  # Botswana
    "BD": "BM",  # Bermuda
    "BE": "BE",  # Belgium (same)
    "BF": "BS",  # Bahamas
    "BG": "BD",  # Bangladesh
    "BH": "BZ",  # Belize
    "BK": "BA",  # Bosnia and Herzegovina
    "BL": "BO",  # Bolivia
    "BM": "MM",  # Burma/Myanmar
    "BN": "BJ",  # Benin
    "BO": "BY",  # Belarus
    "BP": "SB",  # Solomon Islands
    "BR": "BR",  # Brazil (same)
    "BT": "BT",  # Bhutan (same)
    "BU": "BG",  # Bulgaria
    "BV": "BV",  # Bouvet Island (same)
    "BX": "BN",  # Brunei
    "BY": "BI",  # Burundi
    "CA": "CA",  # Canada (same)
    "CB": "KH",  # Cambodia
    "CD": "TD",  # Chad
    "CE": "LK",  # Sri Lanka
    "CF": "CG",  # Congo
    "CG": "CD",  # Zaire/DR Congo
    "CH": "CN",  # China
    "CI": "CL",  # Chile
    "CJ": "KY",  # Cayman Islands
    "CK": "CC",  # Cocos (Keeling) Islands
    "CM": "CM",  # Cameroon (same)
    "CN": "KM",  # Comoros
    "CO": "CO",  # Colombia (same)
    "CQ": "MP",  # Northern Mariana Islands
    "CR": "AU",  # Coral Sea Islands (part of Australia)
    "CS": "CR",  # Costa Rica
    "CT": "CF",  # Central African Republic
    "CU": "CU",  # Cuba (same)
    "CV": "CV",  # Cape Verde (same)
    "CW": "CK",  # Cook Islands
    "CY": "CY",  # Cyprus (same)
    "DA": "DK",  # Denmark
    "DJ": "DJ",  # Djibouti (same)
    "DO": "DM",  # Dominica
    "DR": "DO",  # Dominican Republic
    "EC": "EC",  # Ecuador (same)
    "EG": "EG",  # Egypt (same)
    "EI": "IE",  # Ireland
    "EK": "GQ",  # Equatorial Guinea
    "EN": "EE",  # Estonia
    "ER": "ER",  # Eritrea (same)
    "ES": "SV",  # El Salvador
    "ET": "ET",  # Ethiopia (same)
    "EZ": "CZ",  # Czech Republic
    "FG": "GF",  # French Guiana
    "FI": "FI",  # Finland (same)
    "FJ": "FJ",  # Fiji (same)
    "FK": "FK",  # Falkland Islands (same)
    "FM": "FM",  # Micronesia (same)
    "FO": "FO",  # Faroe Islands (same)
    "FP": "PF",  # French Polynesia
    "FR": "FR",  # France (same)
    "GA": "GM",  # Gambia
    "GB": "GA",  # Gabon
    "GG": "GE",  # Georgia
    "GH": "GH",  # Ghana (same)
    "GI": "GI",  # Gibraltar (same)
    "GJ": "GD",  # Grenada
    "GK": "GG",  # Guernsey
    "GL": "GL",  # Greenland (same)
    "GM": "DE",  # Germany
    "GP": "GP",  # Guadeloupe (same)
    "GQ": "GU",  # Guam
    "GR": "GR",  # Greece (same)
    "GT": "GT",  # Guatemala (same)
    "GV": "GN",  # Guinea
    "GY": "GY",  # Guyana (same)
    "GZ": "PS",  # Gaza Strip (Palestine)
    "HA": "HT",  # Haiti
    "HK": "HK",  # Hong Kong (same)
    "HO": "HN",  # Honduras
    "HR": "HR",  # Croatia (same)
    "HU": "HU",  # Hungary (same)
    "IC": "IS",  # Iceland
    "ID": "ID",  # Indonesia (same)
    "IM": "IM",  # Isle of Man (same)
    "IN": "IN",  # India (same)
    "IO": "IO",  # British Indian Ocean Territory (same)
    "IR": "IR",  # Iran (same)
    "IS": "IL",  # Israel
    "IT": "IT",  # Italy (same)
    "IV": "CI",  # Cote d'Ivoire
    "IZ": "IQ",  # Iraq
    "JA": "JP",  # Japan
    "JE": "JE",  # Jersey (same)
    "JM": "JM",  # Jamaica (same)
    "JN": "SJ",  # Jan Mayen (part of Svalbard and Jan Mayen)
    "JO": "JO",  # Jordan (same)
    "KE": "KE",  # Kenya (same)
    "KG": "KG",  # Kyrgyzstan (same)
    "KN": "KP",  # North Korea
    "KR": "KI",  # Kiribati
    "KS": "KR",  # South Korea
    "KT": "CX",  # Christmas Island
    "KU": "KW",  # Kuwait
    "KV": "XK",  # Kosovo (unofficial)
    "KZ": "KZ",  # Kazakhstan (same)
    "LA": "LA",  # Laos (same)
    "LE": "LB",  # Lebanon
    "LG": "LV",  # Latvia
    "LH": "LT",  # Lithuania
    "LI": "LR",  # Liberia
    "LO": "SK",  # Slovakia
    "LS": "LI",  # Liechtenstein
    "LT": "LS",  # Lesotho
    "LU": "LU",  # Luxembourg (same)
    "LY": "LY",  # Libya (same)
    "MA": "MG",  # Madagascar
    "MB": "MQ",  # Martinique
    "MC": "MO",  # Macau
    "MD": "MD",  # Moldova (same)
    "MF": "YT",  # Mayotte
    "MG": "MN",  # Mongolia
    "MH": "MS",  # Montserrat
    "MI": "MW",  # Malawi
    "MJ": "ME",  # Montenegro
    "MK": "MK",  # North Macedonia (same)
    "ML": "ML",  # Mali (same)
    "MM": "MM",  # Burma/Myanmar (same)
    "MN": "MC",  # Monaco
    "MO": "MA",  # Morocco
    "MP": "MU",  # Mauritius
    "MR": "MR",  # Mauritania (same)
    "MT": "MT",  # Malta (same)
    "MU": "OM",  # Oman
    "MV": "MV",  # Maldives (same)
    "MX": "MX",  # Mexico (same)
    "MY": "MY",  # Malaysia (same)
    "MZ": "MZ",  # Mozambique (same)
    "NC": "NC",  # New Caledonia (same)
    "NE": "NU",  # Niue
    "NF": "NF",  # Norfolk Island (same)
    "NG": "NE",  # Niger
    "NH": "VU",  # Vanuatu
    "NI": "NG",  # Nigeria
    "NL": "NL",  # Netherlands (same)
    "NO": "NO",  # Norway (same)
    "NP": "NP",  # Nepal (same)
    "NR": "NR",  # Nauru (same)
    "NS": "SR",  # Suriname
    "NU": "NI",  # Nicaragua
    "NZ": "NZ",  # New Zealand (same)
    "OD": "SS",  # South Sudan
    "PA": "PY",  # Paraguay
    "PC": "PN",  # Pitcairn Islands
    "PE": "PE",  # Peru (same)
    "PG": "PG",  # Spratly Islands / Papua New Guinea
    "PK": "PK",  # Pakistan (same)
    "PL": "PL",  # Poland (same)
    "PM": "PA",  # Panama
    "PO": "PT",  # Portugal
    "PP": "PG",  # Papua New Guinea
    "PS": "PW",  # Palau
    "PU": "GW",  # Guinea-Bissau
    "QA": "QA",  # Qatar (same)
    "RE": "RE",  # Reunion (same)
    "RI": "RS",  # Serbia
    "RM": "MH",  # Marshall Islands
    "RO": "RO",  # Romania (same)
    "RP": "PH",  # Philippines
    "RQ": "PR",  # Puerto Rico
    "RS": "RU",  # Russia
    "RW": "RW",  # Rwanda (same)
    "SA": "SA",  # Saudi Arabia (same)
    "SB": "PM",  # St. Pierre and Miquelon
    "SC": "KN",  # St. Kitts and Nevis
    "SE": "SC",  # Seychelles
    "SF": "ZA",  # South Africa
    "SG": "SN",  # Senegal
    "SH": "SH",  # St. Helena (same)
    "SI": "SI",  # Slovenia (same)
    "SL": "SL",  # Sierra Leone (same)
    "SM": "SM",  # San Marino (same)
    "SN": "SG",  # Singapore
    "SO": "SO",  # Somalia (same)
    "SP": "ES",  # Spain
    "SR": "RS",  # Serbia
    "ST": "LC",  # St. Lucia
    "SU": "SD",  # Sudan
    "SV": "SJ",  # Svalbard
    "SW": "SE",  # Sweden
    "SX": "GS",  # South Georgia
    "SY": "SY",  # Syria (same)
    "SZ": "CH",  # Switzerland
    "TC": "AE",  # United Arab Emirates
    "TD": "TT",  # Trinidad and Tobago
    "TH": "TH",  # Thailand (same)
    "TI": "TJ",  # Tajikistan
    "TK": "TC",  # Turks and Caicos Islands
    "TL": "TK",  # Tokelau
    "TN": "TO",  # Tonga
    "TO": "TG",  # Togo
    "TP": "ST",  # Sao Tome and Principe
    "TS": "TN",  # Tunisia
    "TU": "TR",  # Turkey
    "TV": "TV",  # Tuvalu (same)
    "TW": "TW",  # Taiwan (same)
    "TX": "TM",  # Turkmenistan
    "TZ": "TZ",  # Tanzania (same)
    "UG": "UG",  # Uganda (same)
    "UK": "GB",  # United Kingdom
    "UP": "UA",  # Ukraine
    "US": "US",  # United States (same)
    "UV": "BF",  # Burkina Faso
    "UY": "UY",  # Uruguay (same)
    "UZ": "UZ",  # Uzbekistan (same)
    "VC": "VC",  # St. Vincent and the Grenadines (same)
    "VE": "VE",  # Venezuela (same)
    "VI": "VG",  # Virgin Islands (British)
    "VM": "VN",  # Vietnam
    "VQ": "VI",  # Virgin Islands (U.S.)
    "VT": "VA",  # Vatican City
    "WA": "NA",  # Namibia
    "WE": "PS",  # West Bank (Palestine)
    "WF": "WF",  # Wallis and Futuna (same)
    "WI": "EH",  # Western Sahara
    "WQ": "UM",  # Wake Island (US Minor Outlying Islands)
    "WS": "WS",  # Western Samoa (same)
    "WZ": "SZ",  # Eswatini
    "YM": "YE",  # Yemen
    "ZA": "ZM",  # Zambia
    "ZI": "ZW",  # Zimbabwe
    "ZM": "WS",  # Samoa
}

# Reverse mapping: ISO to FIPS
ISO_TO_FIPS = {v: k for k, v in FIPS_TO_ISO.items()}

# ISO 3166-1 alpha-2 country codes to nicely-formatted country names
# Sourced from the gt package for standardized, display-friendly country names
ISO_COUNTRY_NAMES = {
    "AW": "Aruba",
    "AF": "Afghanistan",
    "AO": "Angola",
    "AL": "Albania",
    "AD": "Andorra",
    "AE": "United Arab Emirates",
    "AR": "Argentina",
    "AM": "Armenia",
    "AS": "American Samoa",
    "AG": "Antigua & Barbuda",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BI": "Burundi",
    "BE": "Belgium",
    "BJ": "Benin",
    "BF": "Burkina Faso",
    "BD": "Bangladesh",
    "BG": "Bulgaria",
    "BH": "Bahrain",
    "BS": "Bahamas",
    "BA": "Bosnia & Herzegovina",
    "BY": "Belarus",
    "BZ": "Belize",
    "BM": "Bermuda",
    "BO": "Bolivia",
    "BR": "Brazil",
    "BB": "Barbados",
    "BN": "Brunei",
    "BT": "Bhutan",
    "BW": "Botswana",
    "CF": "Central African Republic",
    "CA": "Canada",
    "CH": "Switzerland",
    "CL": "Chile",
    "CN": "China",
    "CI": "Côte d'Ivoire",
    "CM": "Cameroon",
    "CD": "Congo (DRC)",
    "CG": "Congo (Republic)",
    "CO": "Colombia",
    "KM": "Comoros",
    "CV": "Cape Verde",
    "CR": "Costa Rica",
    "CU": "Cuba",
    "CW": "Curaçao",
    "KY": "Cayman Islands",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DE": "Germany",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DK": "Denmark",
    "DO": "Dominican Republic",
    "DZ": "Algeria",
    "EC": "Ecuador",
    "EG": "Egypt",
    "ER": "Eritrea",
    "ES": "Spain",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FI": "Finland",
    "FJ": "Fiji",
    "FR": "France",
    "FO": "Faroe Islands",
    "FM": "Micronesia",
    "GA": "Gabon",
    "GB": "United Kingdom",
    "GE": "Georgia",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GN": "Guinea",
    "GM": "Gambia",
    "GW": "Guinea-Bissau",
    "GQ": "Equatorial Guinea",
    "GR": "Greece",
    "GD": "Grenada",
    "GL": "Greenland",
    "GT": "Guatemala",
    "GU": "Guam",
    "GY": "Guyana",
    "HK": "Hong Kong",
    "HN": "Honduras",
    "HR": "Croatia",
    "HT": "Haiti",
    "HU": "Hungary",
    "ID": "Indonesia",
    "IM": "Isle of Man",
    "IN": "India",
    "IE": "Ireland",
    "IR": "Iran",
    "IQ": "Iraq",
    "IS": "Iceland",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JO": "Jordan",
    "JP": "Japan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KG": "Kyrgyzstan",
    "KH": "Cambodia",
    "KI": "Kiribati",
    "KN": "St. Kitts & Nevis",
    "KR": "South Korea",
    "KW": "Kuwait",
    "LA": "Laos",
    "LB": "Lebanon",
    "LR": "Liberia",
    "LY": "Libya",
    "LC": "St. Lucia",
    "LI": "Liechtenstein",
    "LK": "Sri Lanka",
    "LS": "Lesotho",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MO": "Macao",
    "MF": "St. Martin",
    "MA": "Morocco",
    "MC": "Monaco",
    "MD": "Moldova",
    "MG": "Madagascar",
    "MV": "Maldives",
    "MX": "Mexico",
    "MH": "Marshall Islands",
    "MK": "North Macedonia",
    "ML": "Mali",
    "MT": "Malta",
    "MM": "Myanmar",
    "ME": "Montenegro",
    "MN": "Mongolia",
    "MP": "Northern Mariana Islands",
    "MZ": "Mozambique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "MW": "Malawi",
    "MY": "Malaysia",
    "NA": "Namibia",
    "NC": "New Caledonia",
    "NE": "Niger",
    "NG": "Nigeria",
    "NI": "Nicaragua",
    "NL": "Netherlands",
    "NO": "Norway",
    "NP": "Nepal",
    "NR": "Nauru",
    "NZ": "New Zealand",
    "OM": "Oman",
    "PK": "Pakistan",
    "PA": "Panama",
    "PE": "Peru",
    "PH": "Philippines",
    "PW": "Palau",
    "PG": "Papua New Guinea",
    "PL": "Poland",
    "PR": "Puerto Rico",
    "KP": "North Korea",
    "PT": "Portugal",
    "PY": "Paraguay",
    "PS": "Palestine",
    "PF": "French Polynesia",
    "QA": "Qatar",
    "RO": "Romania",
    "RU": "Russia",
    "RW": "Rwanda",
    "SA": "Saudi Arabia",
    "SD": "Sudan",
    "SN": "Senegal",
    "SG": "Singapore",
    "SB": "Solomon Islands",
    "SL": "Sierra Leone",
    "SV": "El Salvador",
    "SM": "San Marino",
    "SO": "Somalia",
    "RS": "Serbia",
    "SS": "South Sudan",
    "ST": "São Tomé & Príncipe",
    "SR": "Suriname",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SE": "Sweden",
    "SZ": "Eswatini",
    "SX": "Sint Maarten",
    "SC": "Seychelles",
    "SY": "Syria",
    "TC": "Turks & Caicos Islands",
    "TD": "Chad",
    "TG": "Togo",
    "TH": "Thailand",
    "TJ": "Tajikistan",
    "TM": "Turkmenistan",
    "TL": "East Timor",
    "TO": "Tonga",
    "TT": "Trinidad & Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TV": "Tuvalu",
    "TZ": "Tanzania",
    "UG": "Uganda",
    "UA": "Ukraine",
    "UY": "Uruguay",
    "US": "United States",
    "UZ": "Uzbekistan",
    "VC": "St. Vincent & Grenadines",
    "VE": "Venezuela",
    "VG": "British Virgin Islands",
    "VI": "U.S. Virgin Islands",
    "VN": "Vietnam",
    "VU": "Vanuatu",
    "WS": "Samoa",
    "YE": "Yemen",
    "ZA": "South Africa",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}


# US state and territory codes to names
US_STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
    "AS": "American Samoa",
    "GU": "Guam",
    "MP": "Northern Mariana Islands",
    "PR": "Puerto Rico",
    "VI": "U.S. Virgin Islands",
}


class _CountryCodes:
    """
    Convenience class for accessing ISO country codes via attribute access.

    Provides a clean syntax for specifying country codes in function calls:
        wv.search_stations(country_code=wv.country.DE)
        wv.search_stations(country_code=wv.country.GB)

    All ISO 3166-1 alpha-2 country codes are available as attributes.
    """

    def __getattr__(self, name: str) -> str:
        """Return the ISO country code (same as the attribute name)."""
        code = name.upper()
        if code in ISO_COUNTRY_NAMES:
            return code
        raise AttributeError(
            f"'{code}' is not a valid ISO 3166-1 alpha-2 country code. "
            f"See wv.ISO_COUNTRY_NAMES for valid codes."
        )

    def __dir__(self):
        """Return list of all valid ISO country codes for autocomplete."""
        return list(ISO_COUNTRY_NAMES.keys())

    def __repr__(self) -> str:
        return f"<CountryCodes: {len(ISO_COUNTRY_NAMES)} ISO 3166-1 alpha-2 codes>"


# Singleton instance for convenient attribute-based country code access
country = _CountryCodes()


class _StateCodes:
    """
    Convenience class for accessing US state and territory codes via attribute access.

    Provides a clean syntax for specifying state codes in function calls:
        wv.search_stations(state=wv.state.CA)
        wv.search_stations(state=wv.state.NY)
        wv.search_stations(state=wv.state.TX)

    All US state and territory codes are available as attributes.
    Includes the 50 states, DC, and 5 territories (AS, GU, MP, PR, VI).
    """

    def __getattr__(self, name: str) -> str:
        """Return the US state code (same as the attribute name)."""
        code = name.upper()
        if code in US_STATE_NAMES:
            return code
        raise AttributeError(
            f"'{code}' is not a valid US state or territory code. "
            f"See wv.US_STATE_NAMES for valid codes."
        )

    def __dir__(self):
        """Return list of all valid US state codes for autocomplete."""
        return list(US_STATE_NAMES.keys())

    def __repr__(self) -> str:
        return f"<StateCodes: {len(US_STATE_NAMES)} US states and territories>"


# Singleton instance for convenient attribute-based state code access
state = _StateCodes()
