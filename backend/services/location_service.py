import math
from typing import Optional, Tuple
from backend.core.logging import logger

# Curated reference coordinates for prominent Bengaluru civic zones & landmarks
BENGALURU_LANDMARKS = {
    "bmsit": (13.1345, 77.5682, "BMS Institute of Technology, Doddaballapur Road, Yelahanka"),
    "yelahanka": (13.1007, 77.5963, "Yelahanka Satellite Town, Bengaluru"),
    "hebbal": (13.0358, 77.5970, "Hebbal Flyover Junction, Bengaluru"),
    "indiranagar": (12.9784, 77.6408, "100 Feet Road, Indiranagar, Bengaluru"),
    "koramangala": (12.9352, 77.6245, "Sony World Signal, Koramangala, Bengaluru"),
    "whitefield": (12.9698, 77.7500, "ITPB Main Road, Whitefield, Bengaluru"),
    "majestic": (12.9767, 77.5713, "KSR City Railway Station, Majestic, Bengaluru"),
    "mg road": (12.9756, 77.6066, "Mahatma Gandhi Road, Bengaluru"),
    "btm": (12.9166, 77.6101, "BTM Layout 2nd Stage, Bengaluru"),
    "jayanagar": (12.9308, 77.5838, "4th Block, Jayanagar, Bengaluru"),
    "electronic city": (12.8452, 77.6602, "Electronic City Phase 1, Bengaluru"),
    "malleswaram": (13.0031, 77.5643, "8th Cross, Malleswaram, Bengaluru"),
    "rajajinagar": (12.9982, 77.5530, "Navrang Theatre Circle, Rajajinagar, Bengaluru"),
    "bellandur": (12.9304, 77.6784, "Bellandur Outer Ring Road, Bengaluru"),
    "marathahalli": (12.9591, 77.6974, "Marathahalli Bridge, Bengaluru"),
}

DEFAULT_BENGALURU_CENTER = (12.9716, 77.5946, "Bengaluru City Center")

class LocationService:
    def geocode(self, query: str) -> Tuple[float, float, str]:
        """Resolves an address or landmark to latitude, longitude and canonical address."""
        if not query:
            return DEFAULT_BENGALURU_CENTER

        query_lower = query.lower()
        for key, (lat, lon, address) in BENGALURU_LANDMARKS.items():
            if key in query_lower:
                logger.info(f"Geocoded landmark '{key}' -> ({lat}, {lon})")
                return lat, lon, address

        # If not in reference set, return city center with offset derived from query hash for deterministic distinct positioning
        hash_val = sum(ord(c) for c in query)
        offset_lat = ((hash_val % 50) - 25) * 0.002
        offset_lon = (((hash_val // 50) % 50) - 25) * 0.002
        lat = round(DEFAULT_BENGALURU_CENTER[0] + offset_lat, 4)
        lon = round(DEFAULT_BENGALURU_CENTER[1] + offset_lon, 4)
        return lat, lon, f"{query}, Bengaluru"

    def haversine_distance_meters(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates spherical distance between two coordinates in meters."""
        R = 6371000  # Radius of Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

location_service = LocationService()
