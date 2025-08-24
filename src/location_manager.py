#!/usr/bin/env python3
"""
Location Manager for JobSprint
Handles country-specific location filtering with focus on Canada
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class LocationManager:
    """Manages location-specific job search configurations"""
    
    def __init__(self):
        self.locations = self._initialize_locations()
    
    def _initialize_locations(self) -> Dict:
        """Initialize comprehensive location database"""
        return {
            "canada": {
                "country_code": "CA",
                "remote_keywords": [
                    "Canada Remote",
                    "Remote Canada",
                    "Remote - Canada",
                    "Canada (Remote)",
                    "Remote, Canada",
                    "Anywhere in Canada",
                    "Canada-wide Remote"
                ],
                "provinces": {
                    "ontario": {
                        "code": "ON",
                        "cities": [
                            "Toronto, ON",
                            "Toronto, Ontario",
                            "Ottawa, ON", 
                            "Ottawa, Ontario",
                            "Mississauga, ON",
                            "Hamilton, ON",
                            "London, ON",
                            "Kitchener, ON",
                            "Windsor, ON",
                            "Oshawa, ON",
                            "Barrie, ON",
                            "Guelph, ON",
                            "Kingston, ON",
                            "Thunder Bay, ON"
                        ],
                        "remote": [
                            "Ontario Remote",
                            "Remote Ontario",
                            "Remote - Ontario",
                            "Ontario (Remote)"
                        ]
                    },
                    "quebec": {
                        "code": "QC",
                        "cities": [
                            "Montreal, QC",
                            "Montreal, Quebec",
                            "Montréal, QC",
                            "Quebec City, QC",
                            "Laval, QC",
                            "Gatineau, QC",
                            "Longueuil, QC",
                            "Sherbrooke, QC",
                            "Saguenay, QC",
                            "Trois-Rivières, QC"
                        ],
                        "remote": [
                            "Quebec Remote",
                            "Remote Quebec",
                            "Remote - Quebec",
                            "Quebec (Remote)",
                            "QC Remote"
                        ]
                    },
                    "british_columbia": {
                        "code": "BC",
                        "cities": [
                            "Vancouver, BC",
                            "Vancouver, British Columbia",
                            "Surrey, BC",
                            "Burnaby, BC",
                            "Richmond, BC",
                            "Abbotsford, BC",
                            "Coquitlam, BC",
                            "Kelowna, BC",
                            "Saanich, BC",
                            "Langley, BC",
                            "Delta, BC",
                            "North Vancouver, BC",
                            "Kamloops, BC",
                            "Nanaimo, BC",
                            "Victoria, BC"
                        ],
                        "remote": [
                            "BC Remote",
                            "British Columbia Remote",
                            "Remote BC",
                            "Remote - BC",
                            "BC (Remote)"
                        ]
                    },
                    "alberta": {
                        "code": "AB",
                        "cities": [
                            "Calgary, AB",
                            "Calgary, Alberta",
                            "Edmonton, AB",
                            "Edmonton, Alberta",
                            "Red Deer, AB",
                            "Lethbridge, AB",
                            "Medicine Hat, AB",
                            "Grande Prairie, AB"
                        ],
                        "remote": [
                            "Alberta Remote",
                            "Remote Alberta",
                            "AB Remote",
                            "Remote - Alberta"
                        ]
                    },
                    "nova_scotia": {
                        "code": "NS",
                        "cities": [
                            "Halifax, NS",
                            "Halifax, Nova Scotia",
                            "Sydney, NS",
                            "Dartmouth, NS",
                            "Truro, NS"
                        ],
                        "remote": [
                            "Nova Scotia Remote",
                            "Remote Nova Scotia",
                            "NS Remote",
                            "Remote - NS"
                        ]
                    },
                    "new_brunswick": {
                        "code": "NB",
                        "cities": [
                            "Saint John, NB",
                            "Moncton, NB",
                            "Fredericton, NB"
                        ],
                        "remote": [
                            "New Brunswick Remote",
                            "NB Remote",
                            "Remote - NB"
                        ]
                    },
                    "manitoba": {
                        "code": "MB",
                        "cities": [
                            "Winnipeg, MB",
                            "Winnipeg, Manitoba",
                            "Brandon, MB"
                        ],
                        "remote": [
                            "Manitoba Remote",
                            "MB Remote",
                            "Remote - Manitoba"
                        ]
                    },
                    "saskatchewan": {
                        "code": "SK",
                        "cities": [
                            "Saskatoon, SK",
                            "Regina, SK",
                            "Prince Albert, SK"
                        ],
                        "remote": [
                            "Saskatchewan Remote",
                            "SK Remote",
                            "Remote - Saskatchewan"
                        ]
                    },
                    "prince_edward_island": {
                        "code": "PE",
                        "cities": [
                            "Charlottetown, PE"
                        ],
                        "remote": [
                            "PEI Remote",
                            "PE Remote",
                            "Prince Edward Island Remote"
                        ]
                    },
                    "newfoundland": {
                        "code": "NL",
                        "cities": [
                            "St. John's, NL",
                            "Corner Brook, NL"
                        ],
                        "remote": [
                            "Newfoundland Remote",
                            "NL Remote",
                            "Remote - NL"
                        ]
                    }
                }
            },
            "usa": {
                "country_code": "US",
                "remote_keywords": [
                    "United States Remote",
                    "USA Remote",
                    "Remote USA",
                    "Remote - USA",
                    "US Remote",
                    "Remote US"
                ],
                "major_cities": [
                    "New York, NY",
                    "San Francisco, CA",
                    "Seattle, WA",
                    "Austin, TX",
                    "Boston, MA",
                    "Chicago, IL",
                    "Los Angeles, CA",
                    "Denver, CO",
                    "Atlanta, GA",
                    "Miami, FL"
                ]
            },
            "india": {
                "country_code": "IN",
                "remote_keywords": [
                    "India Remote",
                    "Remote India",
                    "Remote - India"
                ],
                "major_cities": [
                    "Bangalore, India",
                    "Mumbai, India",
                    "Delhi, India",
                    "Hyderabad, India",
                    "Chennai, India",
                    "Pune, India",
                    "Kolkata, India"
                ]
            }
        }
    
    def get_canada_locations(self, include_remote: bool = True) -> List[str]:
        """Get all Canada-specific locations"""
        locations = []
        
        if include_remote:
            locations.extend(self.locations["canada"]["remote_keywords"])
        
        # Add all Canadian cities
        for province_data in self.locations["canada"]["provinces"].values():
            locations.extend(province_data["cities"])
            if include_remote:
                locations.extend(province_data["remote"])
        
        return locations
    
    def get_province_locations(self, province: str, include_remote: bool = True) -> List[str]:
        """Get locations for a specific Canadian province"""
        if province not in self.locations["canada"]["provinces"]:
            return []
        
        province_data = self.locations["canada"]["provinces"][province]
        locations = province_data["cities"].copy()
        
        if include_remote:
            locations.extend(province_data["remote"])
        
        return locations
    
    def get_ultra_recent_time_filters(self) -> Dict[str, str]:
        """Get time filters for ultra-recent job searches"""
        return {
            "last_5_minutes": "r300",
            "last_10_minutes": "r600", 
            "last_15_minutes": "r900",
            "last_30_minutes": "r1800",
            "last_1_hour": "r3600",
            "last_2_hours": "r7200",
            "last_6_hours": "r21600",
            "last_24_hours": "r86400"
        }
    
    def get_work_type_filters(self) -> Dict[str, str]:
        """Get work type filters"""
        return {
            "on_site": "1",
            "remote": "2", 
            "hybrid": "3"
        }
    
    def get_recommended_canada_search_locations(self) -> List[str]:
        """Get recommended locations for Canada job searches"""
        return [
            # National remote
            "Canada Remote",
            "Remote Canada",
            
            # Major cities
            "Toronto, ON",
            "Montreal, QC", 
            "Vancouver, BC",
            "Calgary, AB",
            "Ottawa, ON",
            "Edmonton, AB",
            "Halifax, NS",
            
            # Province-wide remote
            "Ontario Remote",
            "Quebec Remote", 
            "BC Remote",
            "Alberta Remote"
        ]
    
    def optimize_location_for_search(self, location: str, country_focus: str = "canada") -> str:
        """Optimize location string for better search results"""
        location = location.strip()
        
        if country_focus == "canada":
            # Handle common variations
            location_mappings = {
                "toronto": "Toronto, ON",
                "montreal": "Montreal, QC",
                "vancouver": "Vancouver, BC",
                "calgary": "Calgary, AB",
                "ottawa": "Ottawa, ON",
                "edmonton": "Edmonton, AB",
                "halifax": "Halifax, NS",
                "remote": "Canada Remote",
                "canada": "Canada Remote"
            }
            
            location_lower = location.lower()
            if location_lower in location_mappings:
                return location_mappings[location_lower]
        
        return location
    
    def is_canada_location(self, location: str) -> bool:
        """Check if a location is Canada-specific"""
        location_lower = location.lower()
        canada_indicators = [
            "canada", "ontario", "quebec", "british columbia", "bc", "alberta", 
            "nova scotia", "ns", "new brunswick", "nb", "manitoba", "mb",
            "saskatchewan", "sk", "prince edward island", "pei", "pe",
            "newfoundland", "nl", "toronto", "montreal", "vancouver", 
            "calgary", "ottawa", "edmonton", "halifax", "on", "qc", "ab"
        ]
        
        return any(indicator in location_lower for indicator in canada_indicators)

# Global instance
location_manager = LocationManager()

def test_location_manager():
    """Test the location manager"""
    print("🌍 Testing Location Manager...")
    
    lm = LocationManager()
    
    # Test Canada locations
    canada_locations = lm.get_canada_locations()
    print(f"📍 Canada locations: {len(canada_locations)}")
    print(f"Sample: {canada_locations[:5]}")
    
    # Test time filters
    time_filters = lm.get_ultra_recent_time_filters()
    print(f"⏰ Time filters: {time_filters}")
    
    # Test recommended locations
    recommended = lm.get_recommended_canada_search_locations()
    print(f"🎯 Recommended Canada locations: {recommended}")
    
    print("✅ Location Manager working!")

if __name__ == "__main__":
    test_location_manager()
