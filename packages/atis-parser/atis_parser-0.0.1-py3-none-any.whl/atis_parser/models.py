"""
Pydantic schema definitions for ATIS, METAR, and TAF parsing.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CloudLayer(BaseModel):
    """Cloud layer information."""
    cloud_type: str = Field(description="Type of cloud layer (e.g., FEW, SCT, BKN, OVC)")
    altitude: int = Field(description="Cloud layer altitude in feet")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class RunwayInfo(BaseModel):
    """Runway information from ATIS."""
    name: str = Field(description="Runway identifier (e.g., '24L', '23', '15R')")
    runway_type: str = Field(description="Type of runway operation (e.g., 'ILS', 'VOR', 'GPS')")
    is_approach: bool = Field(description="Whether this runway is being used for arrivals/approaches")
    is_departure: bool = Field(description="Whether this runway is being used for departures")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class RunwaySurfaceConditionData(BaseModel):
    """Runway Surface Condition (RSC) data for a specific runway."""
    wet_percentage: Optional[int] = Field(None, description="Percentage of runway that is wet (0-100)")
    dry_snow_percentage: Optional[int] = Field(None, description="Percentage of runway with dry snow (0-100)")
    compacted_snow_percentage: Optional[int] = Field(None, description="Percentage of runway with compacted snow (0-100)")
    ice_percentage: Optional[int] = Field(None, description="Percentage of runway with ice (0-100)")
    width: Optional[int] = Field(None, description="Width of runway in feet")
    remaining_width_condition: Optional[str] = Field(None, description="Condition description for remaining width")
    remarks: Optional[str] = Field(None, description="Additional remarks about the runway condition")
    depth_departure: Optional[str] = Field(None, description="Snow/ice depth at departure end (e.g., '5')")
    depth_threshold: Optional[str] = Field(None, description="Snow/ice depth at threshold (e.g., '5')")
    depth_mid: Optional[str] = Field(None, description="Snow/ice depth at mid-point (e.g., '6')")
    condition_departure: Optional[str] = Field(None, description="Condition description at departure end")
    condition_threshold: Optional[str] = Field(None, description="Condition description at threshold")
    condition_mid: Optional[str] = Field(None, description="Condition description at mid-point")
    reported_at: Optional[str] = Field(None, description="Timestamp from RSC report (e.g., '1931Z')")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class AtisParsedData(BaseModel):
    """Structured ATIS data parsed from raw text."""
    wind_direction: int = Field(description="Wind direction in degrees (0-360)")
    wind_speed: int = Field(description="Wind speed in knots")
    visibility: int = Field(description="Visibility in statute miles")
    temperature: int = Field(description="Temperature in Celsius")
    dewpoint: int = Field(description="Dewpoint in Celsius")
    runway_visual_range: Optional[int] = Field(None, description="Runway visual range in feet")
    runway_condition: Optional[Dict[str, RunwaySurfaceConditionData]] = Field(
        default=None,
        description="Runway Surface Condition (RSC) data keyed by runway name (e.g., '23', '24L'). Return empty dict {} if no RSC data is available."
    )
    cloud_layers: List[CloudLayer] = Field(description="List of cloud layers. Return empty list [] if no cloud layers are reported.")
    runways: List[RunwayInfo] = Field(description="List of runways with approach/departure status. Return empty list [] if no runways are mentioned.")
    notams: List[str] = Field(description="List of NOTAMs. Return empty list [] if no NOTAMs are present.")
    remarks: List[str] = Field(description="Additional remarks. Return empty list [] if no remarks are present.")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class MetarParsedData(BaseModel):
    """Structured METAR data parsed from raw text."""
    station: str = Field(description="ICAO station identifier (e.g., 'CYYZ')")
    report_type: Optional[str] = Field(None, description="Report type (e.g., 'SPECI', 'METAR')")
    time: Optional[str] = Field(None, description="Observation time (e.g., '051326Z')")
    wind_direction: Optional[int] = Field(None, description="Wind direction in degrees (0-360)")
    wind_speed: Optional[int] = Field(None, description="Wind speed in knots")
    wind_gust: Optional[int] = Field(None, description="Wind gust speed in knots")
    visibility: Optional[float] = Field(None, description="Visibility in statute miles")
    runway_visual_range: Optional[Dict[str, str]] = Field(
        default=None,
        description="Runway visual range data keyed by runway name"
    )
    weather_phenomena: List[str] = Field(default_factory=list, description="Weather phenomena (e.g., 'SN', 'BR')")
    cloud_layers: List[CloudLayer] = Field(default_factory=list, description="List of cloud layers")
    temperature: Optional[int] = Field(None, description="Temperature in Celsius")
    dewpoint: Optional[int] = Field(None, description="Dewpoint in Celsius")
    altimeter: Optional[str] = Field(None, description="Altimeter setting (e.g., 'A2993')")
    remarks: List[str] = Field(default_factory=list, description="Remarks section")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class TafTimeGroup(BaseModel):
    """Time group in TAF forecast."""
    start_time: str = Field(description="Start time (e.g., '0512')")
    end_time: Optional[str] = Field(None, description="End time (e.g., '0618')")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class TafForecastGroup(BaseModel):
    """Individual forecast group in TAF."""
    time_group: Optional[TafTimeGroup] = Field(None, description="Time group for this forecast")
    modifier: Optional[str] = Field(None, description="Modifier (e.g., 'TEMPO', 'BECMG', 'FM', 'PROB30', 'PROB40')")
    wind_direction: Optional[int] = Field(None, description="Wind direction in degrees")
    wind_speed: Optional[int] = Field(None, description="Wind speed in knots")
    wind_gust: Optional[int] = Field(None, description="Wind gust speed in knots")
    visibility: Optional[str] = Field(None, description="Visibility (e.g., '1/2SM', '5SM', 'P6SM')")
    weather_phenomena: List[str] = Field(default_factory=list, description="Weather phenomena")
    cloud_layers: List[CloudLayer] = Field(default_factory=list, description="Cloud layers")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class TafParsedData(BaseModel):
    """Structured TAF data parsed from raw text."""
    station: str = Field(description="ICAO station identifier")
    report_type: Optional[str] = Field(None, description="Report type (e.g., 'TAF', 'TAF AMD')")
    issue_time: Optional[str] = Field(None, description="Issue time (e.g., '051239Z')")
    valid_period: Optional[str] = Field(None, description="Valid period (e.g., '0512/0618')")
    forecasts: List[TafForecastGroup] = Field(default_factory=list, description="List of forecast groups")
    remarks: List[str] = Field(default_factory=list, description="Remarks section")
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()

