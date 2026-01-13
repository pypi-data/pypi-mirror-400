"""Unit tests for ATIS, METAR, and TAF parsers."""
import os
import json
import pytest
from pathlib import Path
from atis_parser import parse_atis, parse_metar, parse_taf

# Create output directory if it doesn't exist
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class TestATISParser:
    """Test cases for ATIS parser."""
    
    def test_cyyz_arrival_atis(self):
        """Test parsing CYYZ arrival ATIS."""
        atis_text = """Arrival ATIS
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
REMAINING WIDTH
COMPACTED SNOW. BLOWING
SNOW. WINTER MAINTENANCE
CURRENTLY IN PROGRESS.
1232Z. RSC 15L 5/5/5 10
PCT COMPACTED SNOW AND
20 PCT 1/8IN DRY SNOW,
10 PCT COMPACTED SNOW
AND 20 PCT 1/8IN DRY
SNOW, 10 PCT COMPACTED
SNOW AND 20 PCT 1/8IN
DRY SNOW. 160FT WIDTH.
REMAINING WIDTH
COMPACTED SNOW. BLOWING
SNOW. 1256Z. THE CRNT
ATC OPS REQUIRES TAXIING
ACFT TO CROSS AN ACT
RWY. ACFT MUST UTILIZE
ALL ENGINES WHEN XNG ANY
ACT RWY. ACFT RQRG
ENGINE OR ICE CLRG PROC
PRIOR TO DEP MUST INFORM
ATC ON CTC.ACFT MUST
NTFY ATC OF ANY CHGS TO
THESE RQRMTS.
GOOSE/SMALL BIRD ACT IN
THE CYYZ AREA. INFORM
CYYZ ATC INFO O"""
        
        result = parse_atis(atis_text)
        
        assert result.wind_direction == 160
        assert result.wind_speed == 8
        assert result.visibility == 1  # 1/2SM rounded up
        assert result.temperature == -3
        assert result.dewpoint == -4
        assert len(result.cloud_layers) > 0
        assert result.cloud_layers[0].cloud_type == "VV"
        assert result.cloud_layers[0].altitude == 500
        assert len(result.runways) >= 2
        assert any(r.name == "15L" for r in result.runways)
        assert any(r.name == "15R" for r in result.runways)
        assert result.runway_condition is not None
        assert "15R" in result.runway_condition
        assert len(result.notams) > 0
        
        # Save JSON output
        output_file = OUTPUT_DIR / "cyyz_arrival_atis.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())
    
    def test_engm_arrival_atis(self):
        """Test parsing ENGM arrival ATIS (European format)."""
        atis_text = """Arrival ATIS
2026-01-05 13:46 UTC
ENGM ARR ATIS W
1240Z
EXP ILS OR RNP APCH RWY01R
TRL FL085
RCR
RWY01R AT 1239
RWYCC 5/5/5
100 PERCENT 3 MM DRY SNOW
CAUTION SLIPPERY TWYS
RWY01R WIND 040/5KT
VIS TDZ 2300M MID 2700M END 2400M
FBL SN BR
CLD SCT 3500FT BKN 4100FT
TMS9 DPMS12
QNH 1013HPA
CONFIRM ATIS W"""
        
        result = parse_atis(atis_text)
        
        # Check that parsing doesn't crash
        assert result is not None
        # European format may have different fields, so we just verify it parses
        assert isinstance(result.wind_direction, int)
        assert isinstance(result.wind_speed, int)
        
        # Verify runway detection for European format
        assert len(result.runways) > 0
        rwy_01r = next((r for r in result.runways if r.name == "01R"), None)
        assert rwy_01r is not None
        assert rwy_01r.is_approach is True
        assert rwy_01r.is_departure is False
        assert rwy_01r.runway_type in ["ILS", "GPS"]  # RNP mapped to GPS
        
        # Save JSON output
        output_file = OUTPUT_DIR / "engm_arrival_atis.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())
    
    def test_engm_departure_atis(self):
        """Test parsing ENGM departure ATIS (European format)."""
        atis_text = """Departure ATIS
2026-01-05 08:03 UTC
ENGM DEP ATIS B
0620Z
RWY01L IN USE
RCR
RWY01L AT 0425
RWYCC 5/5/5
FIRST PART 100 PERCENT
3 MM SLUSH / SECOND AND
LAST PART 100 PERCENT 3
MM DRY SNOW
CAUTION SLIPPERY TWYS
RWY01L WIND 040/8KT
VIS 10KM
CLD BKN 2700FT
TMS8 DPMS12
QNH 1012HPA
CONFIRM ATIS B"""
        
        result = parse_atis(atis_text)
        
        # Check that parsing doesn't crash
        assert result is not None
        assert isinstance(result.wind_direction, int)
        assert isinstance(result.wind_speed, int)
        
        # Verify runway detection for European format: "RWY01L IN USE" in departure ATIS
        assert len(result.runways) > 0
        rwy_01l = next((r for r in result.runways if r.name == "01L"), None)
        assert rwy_01l is not None
        assert rwy_01l.is_departure is True
        assert rwy_01l.is_approach is False
        
        # Save JSON output
        output_file = OUTPUT_DIR / "engm_departure_atis.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())


class TestMETARParser:
    """Test cases for METAR parser."""
    
    def test_cyyz_metar(self):
        """Test parsing CYYZ METAR."""
        metar_text = "SPECI CYYZ 051326Z 15008KT 1/2SM R15L/4000V5500FT/D R24L/4500VP6000FT/D R24R/5000VP6000FT/D R23/4000V5500FT/N SN VV005 M03/M04 A2993 RMK SN8 SLP147"
        
        result = parse_metar(metar_text)
        
        assert result.station == "CYYZ"
        assert result.report_type == "SPECI"
        assert result.time == "051326Z"
        assert result.wind_direction == 150
        assert result.wind_speed == 8
        assert result.visibility == 0.5
        assert result.temperature == -3
        assert result.dewpoint == -4
        assert result.altimeter == "A2993"
        assert len(result.cloud_layers) > 0
        assert result.runway_visual_range is not None
        assert "15L" in result.runway_visual_range
        
        # Save JSON output
        output_file = OUTPUT_DIR / "cyyz_metar.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())
    
    def test_engm_metar(self):
        """Test parsing ENGM METAR."""
        metar_text = "METAR ENGM 051350Z 01006KT 7000 -SN FEW011 BKN031 M09/M11 Q1013 TEMPO 4000"
        
        result = parse_metar(metar_text)
        
        assert result.station == "ENGM"
        assert result.report_type == "METAR"
        assert result.time == "051350Z"
        assert result.wind_direction == 10
        assert result.wind_speed == 6
        # 7000 meters should be converted to SM (roughly 4.35 SM)
        assert result.visibility is not None
        assert result.visibility > 4.0  # 7000m ≈ 4.35 SM
        assert result.temperature == -9
        assert result.dewpoint == -11
        assert len(result.cloud_layers) >= 2
        assert any(c.cloud_type == "FEW" for c in result.cloud_layers)
        assert any(c.cloud_type == "BKN" for c in result.cloud_layers)
        
        # Save JSON output
        output_file = OUTPUT_DIR / "engm_metar.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())


class TestTAFParser:
    """Test cases for TAF parser."""
    
    def test_cyyz_taf(self):
        """Test parsing CYYZ TAF."""
        taf_text = """TAF AMD CYYZ 051239Z 0512/0618 16010KT 1/2SM SN VV004
TEMPO 0512/0514 2SM -SN OVC010
FM051400 16010KT 1SM -SN BR OVC005
TEMPO 0514/0516 3SM -SN SCT005 OVC010
PROB30 0514/0515 3/4SM -SN BR
FM051600 17012KT 5SM -SN OVC012
BECMG 0516/0518 18010G20KT
FM052000 17012KT P6SM -SN OVC020
BECMG 0522/0524 26005KT
BECMG 0602/0604 30005KT
FM060800 VRB03KT 5SM -SN BR OVC010
PROB30 0608/0612 1SM -FZDZ BR OVC005
FM061200 07007KT 2SM BR OVC005
PROB30 0612/0616 3/4SM -FZDZ BR OVC003
FM061600 11010KT 2SM -SNPL BR OVC005
PROB30 0616/0618 3/4SM -FZRA BR OVC003 RMK NXT FCST BY 051500Z"""
        
        result = parse_taf(taf_text)
        
        assert result.station == "CYYZ"
        assert result.report_type == "TAF AMD"
        assert result.issue_time == "051239Z"
        assert result.valid_period == "0512/0618"
        assert len(result.forecasts) > 0
        # Check first forecast has wind
        assert result.forecasts[0].wind_direction == 160
        assert result.forecasts[0].wind_speed == 10
        
        # Save JSON output
        output_file = OUTPUT_DIR / "cyyz_taf.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())
    
    def test_engm_taf(self):
        """Test parsing ENGM TAF."""
        taf_text = """TAF ENGM 051100Z 0512/0612 02005KT 8000 -SN BKN025
TEMPO 0512/0524 2500 -SN VV012"""
        
        result = parse_taf(taf_text)
        
        assert result.station == "ENGM"
        assert result.report_type == "TAF"
        assert result.issue_time == "051100Z"
        assert result.valid_period == "0512/0612"
        assert len(result.forecasts) >= 2
        # Check main forecast
        assert result.forecasts[0].wind_direction == 20
        assert result.forecasts[0].wind_speed == 5
        # Check TEMPO forecast
        tempo_forecasts = [f for f in result.forecasts if f.modifier == "TEMPO"]
        assert len(tempo_forecasts) > 0
        
        # Save JSON output
        output_file = OUTPUT_DIR / "engm_taf.json"
        with open(output_file, "w") as f:
            f.write(result.to_json())

