"""
Regex-based parsers for ATIS, METAR, and TAF aviation weather reports.
"""
import re
import math
from typing import Optional, Dict, List, Tuple
from .models import (
    AtisParsedData,
    MetarParsedData,
    TafParsedData,
    CloudLayer,
    RunwayInfo,
    RunwaySurfaceConditionData,
    TafForecastGroup,
    TafTimeGroup,
)


def _parse_wind(wind_str: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Parse wind string (e.g., '16008KT', '28011KT', 'VRB03KT')."""
    if not wind_str:
        return None, None, None
    
    # Variable wind
    if wind_str.startswith('VRB'):
        match = re.match(r'VRB(\d+)KT', wind_str)
        if match:
            return None, int(match.group(1)), None
        return None, None, None
    
    # Standard wind with optional gust
    match = re.match(r'(\d{3})(\d{2,3})(?:G(\d{2,3}))?KT', wind_str)
    if match:
        direction = int(match.group(1))
        speed = int(match.group(2))
        gust = int(match.group(3)) if match.group(3) else None
        return direction, speed, gust
    
    return None, None, None


def _parse_visibility(vis_str: str) -> Optional[float]:
    """Parse visibility string (e.g., '1/2SM', '15SM', 'P6SM')."""
    if not vis_str:
        return None
    
    # Fractional visibility
    match = re.match(r'(\d+)/(\d+)SM', vis_str)
    if match:
        return float(match.group(1)) / float(match.group(2))
    
    # Standard visibility
    match = re.match(r'P?(\d+(?:\.\d+)?)SM', vis_str)
    if match:
        return float(match.group(1))
    
    # Miles without SM (sometimes)
    match = re.match(r'P?(\d+(?:\.\d+)?)', vis_str)
    if match:
        return float(match.group(1))
    
    return None


def _parse_temperature(temp_str: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse temperature/dewpoint string (e.g., 'M03/M04', 'M02/M06')."""
    if not temp_str:
        return None, None
    
    match = re.match(r'([M-]?\d{2})/([M-]?\d{2})', temp_str)
    if match:
        temp = match.group(1)
        dewpoint = match.group(2)
        
        def parse_temp(t: str) -> int:
            if t.startswith('M'):
                return -int(t[1:])
            return int(t)
        
        return parse_temp(temp), parse_temp(dewpoint)
    
    return None, None


def _parse_cloud_layer(cloud_str: str) -> Optional[CloudLayer]:
    """Parse cloud layer string (e.g., 'SCT034', 'BKN050', 'OVC010', 'VV005')."""
    if not cloud_str:
        return None
    
    # Vertical visibility
    match = re.match(r'VV(\d{3})', cloud_str)
    if match:
        return CloudLayer(cloud_type="VV", altitude=int(match.group(1)) * 100)
    
    # Standard cloud layers
    match = re.match(r'(FEW|SCT|BKN|OVC)(\d{3})', cloud_str)
    if match:
        return CloudLayer(
            cloud_type=match.group(1),
            altitude=int(match.group(2)) * 100
        )
    
    return None


def _parse_runway_surface_condition(text: str, runway_name: str) -> Optional[RunwaySurfaceConditionData]:
    """Parse RSC (Runway Surface Condition) data for a runway."""
    rsc_data = RunwaySurfaceConditionData()
    
    # Extract timestamp if present (e.g., "1232Z", "1549Z")
    time_match = re.search(r'(\d{4})Z', text)
    if time_match:
        rsc_data.reported_at = time_match.group(1) + 'Z'
    
    # Parse depth format like "5/5/5" or "6/6/6"
    depth_match = re.search(r'(\d+)/(\d+)/(\d+)', text)
    if depth_match:
        rsc_data.depth_departure = depth_match.group(1)
        rsc_data.depth_threshold = depth_match.group(2)
        rsc_data.depth_mid = depth_match.group(3)
    
    # Parse percentages and conditions
    # Pattern: "30 PCT 1/8IN DRY SNOW" or "100 PCT WET"
    percentage_patterns = [
        (r'(\d+)\s+PCT\s+WET', 'wet_percentage'),
        (r'(\d+)\s+PCT\s+(\d+/\d+IN\s+)?DRY\s+SNOW', 'dry_snow_percentage'),
        (r'(\d+)\s+PCT\s+COMPACTED\s+SNOW', 'compacted_snow_percentage'),
        (r'(\d+)\s+PCT\s+ICE', 'ice_percentage'),
    ]
    
    for pattern, field in percentage_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            pct = int(match.group(1))
            if field == 'wet_percentage':
                rsc_data.wet_percentage = pct
            elif field == 'dry_snow_percentage':
                rsc_data.dry_snow_percentage = pct
            elif field == 'compacted_snow_percentage':
                rsc_data.compacted_snow_percentage = pct
            elif field == 'ice_percentage':
                rsc_data.ice_percentage = pct
    
    # Parse width (e.g., "160FT WIDTH", "180FT WIDTH")
    width_match = re.search(r'(\d+)FT\s+WIDTH', text, re.IGNORECASE)
    if width_match:
        rsc_data.width = int(width_match.group(1))
    
    # Parse remaining width condition
    remaining_match = re.search(r'REMAINING\s+WIDTH\s+([^.]+)', text, re.IGNORECASE)
    if remaining_match:
        rsc_data.remaining_width_condition = remaining_match.group(1).strip()
    
    # Extract additional remarks
    remarks_parts = []
    if 'CHEMICAL RESIDUE' in text.upper():
        remarks_parts.append('CHEMICAL RESIDUE PRESENT')
    if 'CHEMICALLY TREATED' in text.upper():
        remarks_parts.append('CHEMICALLY TREATED')
    if 'BLOWING SNOW' in text.upper():
        remarks_parts.append('BLOWING SNOW')
    
    if remarks_parts:
        rsc_data.remarks = '. '.join(remarks_parts)
    
    return rsc_data


def parse_atis(text: str) -> AtisParsedData:
    """
    Parse ATIS text into structured format.
    
    Args:
        text: Raw ATIS text
        
    Returns:
        AtisParsedData: Parsed ATIS data
    """
    # Normalize text - remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Extract wind (handle both standard and runway-specific European format)
    wind_match = re.search(r'(\d{3}\d{2,3}(?:G\d{2,3})?KT|VRB\d{2,3}KT)', text)
    if not wind_match:
        # Try European runway wind format: "RWY01R WIND 040/5KT"
        rwy_wind_match = re.search(r'RWY\d+[LRC]?\s+WIND\s+(\d{3})/(\d+)KT', text, re.IGNORECASE)
        if rwy_wind_match:
            wind_direction = int(rwy_wind_match.group(1))
            wind_speed = int(rwy_wind_match.group(2))
        else:
            wind_direction, wind_speed = None, None
    else:
        wind_direction, wind_speed, _ = _parse_wind(wind_match.group(1))
    
    # Extract visibility (handle both US and European formats)
    vis_match = re.search(r'(\d+/\d+SM|P?\d+(?:\.\d+)?SM)', text)
    if not vis_match:
        # Try European format: "VIS 10KM" or "VIS TDZ 2300M MID 2700M END 2400M"
        vis_km_match = re.search(r'VIS\s+(\d+)KM', text, re.IGNORECASE)
        if vis_km_match:
            # Convert KM to SM (roughly)
            km = int(vis_km_match.group(1))
            visibility = km * 0.621371
        else:
            visibility = None
    else:
        visibility = _parse_visibility(vis_match.group(1))
    
    # Extract temperature/dewpoint (handle both US and European formats)
    temp_match = re.search(r'([M-]?\d{2}/[M-]?\d{2})', text)
    if temp_match:
        temperature, dewpoint = _parse_temperature(temp_match.group(1))
    else:
        # Try European format: "TMS9 DPMS12" (Temperature Minus 9, Dewpoint Minus 12)
        tms_match = re.search(r'TMS(\d+)', text, re.IGNORECASE)
        dpms_match = re.search(r'DPMS(\d+)', text, re.IGNORECASE)
        if tms_match and dpms_match:
            temperature = -int(tms_match.group(1))
            dewpoint = -int(dpms_match.group(1))
        else:
            temperature, dewpoint = None, None
    
    # Extract altimeter (handle both US and European formats)
    altimeter_match = re.search(r'A(\d{4})', text)
    if altimeter_match:
        altimeter = altimeter_match.group(1)
    else:
        # Try European format: "QNH 1013HPA"
        qnh_match = re.search(r'QNH\s+(\d{4})', text, re.IGNORECASE)
        altimeter = qnh_match.group(1) if qnh_match else None
    
    # Extract cloud layers
    cloud_layers = []
    cloud_matches = re.finditer(r'(FEW|SCT|BKN|OVC|VV)(\d{3})', text)
    for match in cloud_matches:
        cloud_str = match.group(0)
        cloud_layer = _parse_cloud_layer(cloud_str)
        if cloud_layer:
            cloud_layers.append(cloud_layer)
    
    # Extract runways
    runways = []
    
    # Check if this is arrival or departure ATIS
    is_arrival_atis = bool(re.search(r'ARR\s+ATIS|ARRIVAL\s+ATIS', text, re.IGNORECASE))
    is_departure_atis = bool(re.search(r'DEP\s+ATIS|DEPARTURE\s+ATIS', text, re.IGNORECASE))
    
    # Extract European format: "EXP ILS OR RNP APCH RWY01R" (arrival)
    # Pattern: EXP ... APCH RWY{name} - capture runway name and extract approach types
    exp_apch_matches = re.finditer(r'EXP\s+.*?APCH\s+RWY\s*(\d{1,2}[LRC]?)', text, re.IGNORECASE)
    for match in exp_apch_matches:
        runway_name = match.group(1).upper()
        # Extract the approach types from the full match
        full_match = match.group(0)
        # Look for ILS, VOR, GPS, RNAV, or RNP in the match
        approach_types = re.findall(r'\b(ILS|VOR|GPS|RNAV|RNP)\b', full_match, re.IGNORECASE)
        # Map RNP to GPS
        approach_types = [t.upper().replace('RNP', 'GPS') for t in approach_types]
        # Use first approach type, default to ILS
        runway_type = approach_types[0] if approach_types else "ILS"
        
        existing = next((r for r in runways if r.name == runway_name), None)
        if existing:
            existing.is_approach = True
            if not existing.runway_type:
                existing.runway_type = runway_type
        else:
            runways.append(RunwayInfo(
                name=runway_name,
                runway_type=runway_type,
                is_approach=True,
                is_departure=False
            ))
    
    # Extract standard format: "ILS RWY 15L", "VOR RWY 23", etc.
    runway_matches = re.finditer(r'(ILS|VOR|GPS|RNAV)\s+RWY\s+(\d{1,2}[LRC]?)', text, re.IGNORECASE)
    for match in runway_matches:
        runway_type = match.group(1).upper()
        runway_name = match.group(2).upper()
        existing = next((r for r in runways if r.name == runway_name), None)
        if existing:
            existing.is_approach = True
            if not existing.runway_type:
                existing.runway_type = runway_type
        else:
            runways.append(RunwayInfo(
                name=runway_name,
                runway_type=runway_type,
                is_approach=True,
                is_departure=False
            ))
    
    # Extract landing runways: "LDG RWY 15L"
    landing_matches = re.finditer(r'LDG\s+RWY\s+(\d{1,2}[LRC]?)', text, re.IGNORECASE)
    for match in landing_matches:
        runway_name = match.group(1).upper()
        existing = next((r for r in runways if r.name == runway_name), None)
        if existing:
            existing.is_approach = True
        else:
            runways.append(RunwayInfo(
                name=runway_name,
                runway_type="",
                is_approach=True,
                is_departure=False
            ))
    
    # Extract European format: "RWY01L IN USE" (departure)
    rwy_in_use_matches = re.finditer(r'RWY\s*(\d{1,2}[LRC]?)\s+IN\s+USE', text, re.IGNORECASE)
    for match in rwy_in_use_matches:
        runway_name = match.group(1).upper()
        existing = next((r for r in runways if r.name == runway_name), None)
        if existing:
            # If it's a departure ATIS, mark as departure
            if is_departure_atis:
                existing.is_departure = True
        else:
            runways.append(RunwayInfo(
                name=runway_name,
                runway_type="",
                is_approach=False,
                is_departure=is_departure_atis  # True if departure ATIS, False otherwise
            ))
    
    # Extract departure runways: "DEP RWY 15R"
    dep_matches = re.finditer(r'DEP\s+RWY\s+(\d{1,2}[LRC]?)', text, re.IGNORECASE)
    for match in dep_matches:
        runway_name = match.group(1).upper()
        existing = next((r for r in runways if r.name == runway_name), None)
        if existing:
            existing.is_departure = True
        else:
            runways.append(RunwayInfo(
                name=runway_name,
                runway_type="",
                is_approach=False,
                is_departure=True
            ))
    
    # Extract RSC (Runway Surface Condition) data
    runway_conditions = {}
    rsc_matches = re.finditer(r'RSC\s+(\d{1,2}[LRC]?)\s+([^.]*(?:\.|$))', text, re.IGNORECASE)
    for match in rsc_matches:
        runway_name = match.group(1).upper()
        rsc_text = match.group(2)
        
        # Get more context - look for next RSC or end of section
        start_pos = match.end()
        next_rsc = re.search(r'RSC\s+\d{1,2}[LRC]?', text[start_pos:], re.IGNORECASE)
        if next_rsc:
            rsc_text = text[match.start():start_pos + next_rsc.start()]
        else:
            # Take until next major section or end
            rsc_text = text[match.start():match.start() + 500]
        
        rsc_data = _parse_runway_surface_condition(rsc_text, runway_name)
        if rsc_data:
            runway_conditions[runway_name] = rsc_data
    
    # Extract NOTAMs and remarks
    notams = []
    remarks = []
    
    # Look for common NOTAM patterns
    notam_patterns = [
        r'ACFT\s+RQRG\s+ENGINE\s+OR\s+ICE\s+CLRG\s+PROC[^.]*',
        r'ACFT\s+MUST\s+NTFY\s+ATC[^.]*',
        r'GOOSE/SMALL\s+BIRD\s+ACT[^.]*',
        r'THE\s+CRNT\s+ATC\s+OPS[^.]*',
    ]
    
    for pattern in notam_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            notam_text = match.group(0).strip()
            if notam_text and notam_text not in notams:
                notams.append(notam_text)
    
    # Extract PIREPs
    pirep_match = re.search(r'PIREP[^.]*', text, re.IGNORECASE)
    if pirep_match:
        remarks.append(pirep_match.group(0).strip())
    
    # Extract other remarks
    if 'WINTER MAINTENANCE' in text.upper():
        remarks.append('WINTER MAINTENANCE IN PROGRESS')
    
    return AtisParsedData(
        wind_direction=wind_direction or 0,
        wind_speed=wind_speed or 0,
        visibility=math.ceil(visibility) if visibility else 0,
        temperature=temperature or 0,
        dewpoint=dewpoint or 0,
        runway_visual_range=None,
        runway_condition=runway_conditions if runway_conditions else None,
        cloud_layers=cloud_layers,
        runways=runways,
        notams=notams,
        remarks=remarks
    )


def parse_metar(text: str) -> MetarParsedData:
    """
    Parse METAR text into structured format.
    
    Args:
        text: Raw METAR text
        
    Returns:
        MetarParsedData: Parsed METAR data
    """
    # Normalize text
    text = text.strip()
    
    # Extract station
    station_match = re.match(r'(?:SPECI\s+)?(?:METAR\s+)?([A-Z]{4})', text)
    station = station_match.group(1) if station_match else ""
    
    # Extract report type
    report_type_match = re.match(r'(SPECI|METAR)', text)
    report_type = report_type_match.group(1) if report_type_match else None
    
    # Extract time
    time_match = re.search(r'(\d{6})Z', text)
    time = time_match.group(1) + 'Z' if time_match else None
    
    # Extract wind
    wind_match = re.search(r'(\d{3}\d{2,3}(?:G\d{2,3})?KT|VRB\d{2,3}KT)', text)
    wind_direction, wind_speed, wind_gust = _parse_wind(wind_match.group(1) if wind_match else "")
    
    # Extract visibility (must have SM suffix, or be a standalone number before RVR)
    # Look for visibility before RVR section
    vis_match = re.search(r'(\d+/\d+SM|P?\d+(?:\.\d+)?SM)', text)
    visibility = None
    if vis_match:
        vis_str = vis_match.group(1)
        visibility = _parse_visibility(vis_str)
    else:
        # Try meter-based visibility (e.g., "7000" in METAR means 7000 meters)
        # Look for 4-digit number before weather/clouds/RVR
        vis_m_match = re.search(r'\s(\d{4})\s+(?:-?[A-Z]{2}|[A-Z]{2,4}|R\d{2})', text)
        if vis_m_match:
            # Convert meters to statute miles
            meters = int(vis_m_match.group(1))
            visibility = meters / 1609.34
    
    # Extract RVR (Runway Visual Range)
    rvr_data = {}
    rvr_matches = re.finditer(r'R(\d{2}[LRC]?)/(\d{4}(?:V\d{4})?)(?:FT)?/([DNUP])', text)
    for match in rvr_matches:
        runway = match.group(1)
        value = match.group(2)
        trend = match.group(3)
        rvr_data[runway] = f"{value}FT/{trend}"
    
    # Extract weather phenomena
    weather_phenomena = []
    weather_match = re.search(r'([+-]?(?:TS|SH|FZ|BL|DR|MI|BC|PR|RA|DZ|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS))\s+', text)
    if weather_match:
        # Find all weather codes
        weather_codes = re.findall(r'([+-]?(?:TS|SH|FZ|BL|DR|MI|BC|PR|RA|DZ|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS))', text)
        weather_phenomena = list(set(weather_codes))
    
    # Extract cloud layers
    cloud_layers = []
    cloud_matches = re.finditer(r'(FEW|SCT|BKN|OVC|VV)(\d{3})', text)
    for match in cloud_matches:
        cloud_str = match.group(0)
        cloud_layer = _parse_cloud_layer(cloud_str)
        if cloud_layer:
            cloud_layers.append(cloud_layer)
    
    # Extract temperature/dewpoint (look for M prefix or negative, and ensure it's not RVR)
    # Temperature comes after weather/clouds and before altimeter
    temp_match = re.search(r'\s([M-]\d{2})/([M-]\d{2})\s', text)
    if not temp_match:
        # Try without M prefix (positive temps)
        temp_match = re.search(r'\s(-?\d{2})/(-?\d{2})\s+A\d{4}', text)
    temperature, dewpoint = _parse_temperature(temp_match.group(0).strip() if temp_match else "")
    
    # Extract altimeter
    altimeter_match = re.search(r'(A\d{4})', text)
    altimeter = altimeter_match.group(1) if altimeter_match else None
    
    # Extract remarks
    remarks = []
    rmk_match = re.search(r'RMK\s+(.+)', text)
    if rmk_match:
        remarks_text = rmk_match.group(1)
        # Split remarks by common patterns
        remarks = [r.strip() for r in re.split(r'\s+(?=[A-Z]{2,})', remarks_text) if r.strip()]
    
    return MetarParsedData(
        station=station,
        report_type=report_type,
        time=time,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        wind_gust=wind_gust,
        visibility=visibility,
        runway_visual_range=rvr_data if rvr_data else None,
        weather_phenomena=weather_phenomena,
        cloud_layers=cloud_layers,
        temperature=temperature,
        dewpoint=dewpoint,
        altimeter=altimeter,
        remarks=remarks
    )


def parse_taf(text: str) -> TafParsedData:
    """
    Parse TAF text into structured format.
    
    Args:
        text: Raw TAF text
        
    Returns:
        TafParsedData: Parsed TAF data
    """
    # Normalize text - replace newlines with spaces
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Extract station
    station_match = re.match(r'TAF(?:\s+AMD)?\s+([A-Z]{4})', text)
    station = station_match.group(1) if station_match else ""
    
    # Extract report type
    report_type_match = re.match(r'(TAF(?:\s+AMD)?)', text)
    report_type = report_type_match.group(1) if report_type_match else None
    
    # Extract issue time
    issue_match = re.search(r'(\d{6})Z', text)
    issue_time = issue_match.group(1) + 'Z' if issue_match else None
    
    # Extract valid period
    valid_match = re.search(r'(\d{4}/\d{4})', text)
    valid_period = valid_match.group(1) if valid_match else None
    
    # Extract remarks
    remarks = []
    rmk_match = re.search(r'RMK\s+(.+)', text)
    if rmk_match:
        remarks_text = rmk_match.group(1)
        remarks = [r.strip() for r in remarks_text.split() if r.strip()]
    
    # Remove remarks from main text for parsing
    main_text = re.sub(r'RMK\s+.+', '', text)
    
    # Parse forecast groups
    forecasts = []
    
    # Split by forecast modifiers (handle PROB30/PROB40 with optional space)
    forecast_parts = re.split(r'\s+(TEMPO|BECMG|FM|PROB30|PROB40)\s+', main_text)
    
    # First part is the main forecast
    if forecast_parts:
        main_forecast = forecast_parts[0]
        # Remove header info from main forecast
        main_forecast = re.sub(r'^TAF(?:\s+AMD)?\s+[A-Z]{4}\s+\d{6}Z\s+\d{4}/\d{4}\s+', '', main_forecast)
        
        if main_forecast.strip():
            forecast_group = _parse_taf_forecast_group(main_forecast.strip(), None)
            if forecast_group:
                forecasts.append(forecast_group)
    
    # Parse subsequent forecast groups
    i = 1
    while i < len(forecast_parts):
        if i + 1 < len(forecast_parts):
            modifier = forecast_parts[i]
            forecast_text = forecast_parts[i + 1]
            forecast_group = _parse_taf_forecast_group(forecast_text.strip(), modifier)
            if forecast_group:
                forecasts.append(forecast_group)
        i += 2
    
    return TafParsedData(
        station=station,
        report_type=report_type,
        issue_time=issue_time,
        valid_period=valid_period,
        forecasts=forecasts,
        remarks=remarks
    )


def _parse_taf_forecast_group(text: str, modifier: Optional[str]) -> Optional[TafForecastGroup]:
    """Parse a single TAF forecast group."""
    forecast = TafForecastGroup(modifier=modifier)
    
    # Extract time group if present (for FM, TEMPO, etc.)
    if modifier == 'FM':
        time_match = re.match(r'(\d{4})\s+(.+)', text)
        if time_match:
            forecast.time_group = TafTimeGroup(start_time=time_match.group(1))
            text = time_match.group(2)
    elif modifier in ['TEMPO', 'PROB30', 'PROB40']:
        time_match = re.search(r'(\d{4})/(\d{4})', text)
        if time_match:
            forecast.time_group = TafTimeGroup(
                start_time=time_match.group(1),
                end_time=time_match.group(2)
            )
            text = re.sub(r'\d{4}/\d{4}\s+', '', text)
    elif modifier == 'BECMG':
        time_match = re.search(r'(\d{4})/(\d{4})', text)
        if time_match:
            forecast.time_group = TafTimeGroup(
                start_time=time_match.group(1),
                end_time=time_match.group(2)
            )
            text = re.sub(r'\d{4}/\d{4}\s+', '', text)
    
    # Extract wind
    wind_match = re.search(r'(\d{3}\d{2,3}(?:G\d{2,3})?KT|VRB\d{2,3}KT)', text)
    if wind_match:
        wind_direction, wind_speed, wind_gust = _parse_wind(wind_match.group(1))
        forecast.wind_direction = wind_direction
        forecast.wind_speed = wind_speed
        forecast.wind_gust = wind_gust
        text = re.sub(r'\d{3}\d{2,3}(?:G\d{2,3})?KT|VRB\d{2,3}KT', '', text)
    
    # Extract visibility (handle both SM and meter formats)
    vis_match = re.search(r'(\d+/\d+SM|P?\d+(?:\.\d+)?SM)', text)
    if vis_match:
        forecast.visibility = vis_match.group(1)
        text = re.sub(r'\d+/\d+SM|P?\d+(?:\.\d+)?SM', '', text)
    else:
        # Try meter-based visibility (4-digit number, e.g., "8000", "2500")
        vis_m_match = re.search(r'\s(\d{4})\s+(?:-?[A-Z]{2}|[A-Z]{2,4}|VV\d{3})', text)
        if vis_m_match:
            meters = int(vis_m_match.group(1))
            # Convert to SM and format as string
            sm = meters / 1609.34
            forecast.visibility = f"{sm:.1f}SM"
    
    # Extract weather phenomena
    weather_codes = re.findall(r'([+-]?(?:TS|SH|FZ|BL|DR|MI|BC|PR|RA|DZ|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS|FZDZ|FZRA|SNPL))', text)
    forecast.weather_phenomena = list(set(weather_codes))
    
    # Extract cloud layers
    cloud_matches = re.finditer(r'(FEW|SCT|BKN|OVC|VV)(\d{3})', text)
    for match in cloud_matches:
        cloud_str = match.group(0)
        cloud_layer = _parse_cloud_layer(cloud_str)
        if cloud_layer:
            forecast.cloud_layers.append(cloud_layer)
    
    return forecast
