# ATIS Parser

A Python package for parsing ATIS, METAR, and TAF aviation weather reports using regex-based parsing. This package converts raw aviation weather text into structured Pydantic models for easy programmatic access.

## Features

- **ATIS Parser**: Parses Arrival and Departure ATIS reports (supports both North American and European formats)
- **METAR Parser**: Parses METAR (Meteorological Aerodrome Report) observations
- **TAF Parser**: Parses TAF (Terminal Aerodrome Forecast) forecasts
- **Structured Output**: Returns Pydantic models for type safety and validation
- **Comprehensive Parsing**: Extracts wind, visibility, temperature, cloud layers, runway conditions, and more
- **Format Support**: Handles both North American (CYYZ) and European (ENGM) ATIS formats
- **Helper Methods**: Built-in `.to_json()` and `.to_dict()` methods for easy serialization
- **Smart Runway Detection**: Automatically detects arrival and departure runways from various format patterns

## Installation

```bash
pip install atis-parser
```

Or install from source:

```bash
git clone https://github.com/planesfyi/atis_parser.git
cd atis-parser
pip install -e .
```

## Usage

### ATIS Parsing

```python
from atis_parser import parse_atis

atis_text = """
Arrival ATIS
2026-01-05 13:29 UTC
CYYZ ARR ATIS O
1326Z CYYZ ARR ATIS O
1326Z 16008KT 1/2SM SN
VV005 M03/M04 A2993 APCH
ILS RWY 15L. LDG RWY 15L
DEP RWY 15R. RSC 15R
5/5/5 30 PCT 1/8IN DRY
SNOW, 30 PCT 1/8IN DRY
SNOW, 30 PCT 1/8IN DRY
SNOW. 160FT WIDTH.
"""

result = parse_atis(atis_text)
print(result.wind_direction)  # 160
print(result.wind_speed)      # 8
print(result.visibility)     # 1 (for 1/2SM, rounded up)
print(result.temperature)    # -3
print(result.dewpoint)        # -4
print(result.runways)         # List of RunwayInfo objects
print(result.runway_condition)  # Dict of RunwaySurfaceConditionData

# Convert to JSON or dictionary
json_output = result.to_json()  # Returns formatted JSON string
data_dict = result.to_dict()    # Returns Python dictionary
```

### METAR Parsing

```python
from atis_parser import parse_metar

metar_text = "SPECI CYYZ 051326Z 15008KT 1/2SM R15L/4000V5500FT/D R24L/4500VP6000FT/D R24R/5000VP6000FT/D R23/4000V5500FT/N SN VV005 M03/M04 A2993 RMK SN8 SLP147"

result = parse_metar(metar_text)
print(result.station)         # "CYYZ"
print(result.wind_direction)  # 150
print(result.wind_speed)      # 8
print(result.visibility)     # 0.5
print(result.temperature)    # -3
print(result.dewpoint)        # -4
print(result.cloud_layers)   # List of CloudLayer objects
```

### TAF Parsing

```python
from atis_parser import parse_taf

taf_text = """
TAF AMD CYYZ 051239Z 0512/0618 16010KT 1/2SM SN VV004
TEMPO 0512/0514 2SM -SN OVC010
FM051400 16010KT 1SM -SN BR OVC005
"""

result = parse_taf(taf_text)
print(result.station)         # "CYYZ"
print(result.issue_time)      # "051239Z"
print(result.valid_period)    # "0512/0618"
print(result.forecasts)       # List of TafForecastGroup objects
```

## Format Support

The parser supports both **North American** and **European** ATIS formats:

### North American Format (e.g., CYYZ)
- Standard wind format: `16008KT`
- Temperature format: `M03/M04` (negative temperatures)
- Altimeter: `A2993`
- Runway patterns: `ILS RWY 15L`, `LDG RWY 15L`, `DEP RWY 15R`

### European Format (e.g., ENGM)
- Runway-specific wind: `RWY01R WIND 040/5KT`
- Temperature format: `TMS9 DPMS12` (Temperature Minus 9, Dewpoint Minus 12)
- Altimeter: `QNH 1013HPA`
- Visibility: `VIS 10KM` or `VIS TDZ 2300M MID 2700M END 2400M`
- Arrival runways: `EXP ILS OR RNP APCH RWY01R`
- Departure runways: `RWY01L IN USE` (in departure ATIS)

## Data Models

All models include `.to_json(indent=2)` and `.to_dict()` helper methods for easy serialization.

### AtisParsedData

- `wind_direction`: Wind direction in degrees (0-360)
- `wind_speed`: Wind speed in knots
- `visibility`: Visibility in statute miles (rounded up for fractional values)
- `temperature`: Temperature in Celsius
- `dewpoint`: Dewpoint in Celsius
- `runway_condition`: Dictionary of runway surface conditions keyed by runway name
- `cloud_layers`: List of cloud layer information
- `runways`: List of runway information with approach/departure status
- `notams`: List of NOTAMs
- `remarks`: Additional remarks
- `.to_json(indent=2)`: Convert to JSON string
- `.to_dict()`: Convert to Python dictionary

### MetarParsedData

- `station`: ICAO station identifier
- `report_type`: Report type (METAR, SPECI)
- `time`: Observation time
- `wind_direction`, `wind_speed`, `wind_gust`: Wind information
- `visibility`: Visibility in statute miles (supports both SM and meter-based formats)
- `runway_visual_range`: Dictionary of RVR data
- `weather_phenomena`: List of weather codes
- `cloud_layers`: List of cloud layers
- `temperature`, `dewpoint`: Temperature information
- `altimeter`: Altimeter setting
- `remarks`: Remarks section
- `.to_json(indent=2)`: Convert to JSON string
- `.to_dict()`: Convert to Python dictionary

### TafParsedData

- `station`: ICAO station identifier
- `report_type`: Report type (TAF, TAF AMD)
- `issue_time`: Issue time
- `valid_period`: Valid period
- `forecasts`: List of forecast groups with modifiers (TEMPO, BECMG, FM, PROB30, PROB40, etc.)
- `remarks`: Remarks section
- `.to_json(indent=2)`: Convert to JSON string
- `.to_dict()`: Convert to Python dictionary

## Development

### Running Tests

```bash
make test
```

Tests run automatically on push and pull requests via GitHub Actions.

### Building and Publishing

The package is automatically published to PyPI when a GitHub release is created. See [.github/workflows/README.md](.github/workflows/README.md) for setup instructions.

## Requirements

- Python 3.8+
- pydantic >= 2.0.0

## License

MIT License
