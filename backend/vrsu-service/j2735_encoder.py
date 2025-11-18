"""
SAE J2735 Message Encoder for Virtual RSU
==========================================

Generates SAE J2735 standard messages for V2X communication:
- TIM (Traveler Information Message) - Work zone warnings
- RSA (Road Side Alert) - Critical safety alerts

Standards:
- SAE J2735-202309 (September 2023 revision)
- DSRC Message Set Dictionary
- C-V2X compatible encoding

Author: ADBA Labs
Project: QEW Innovation Corridor vRSU
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Position:
    """GPS position in SAE J2735 format"""
    lat: float  # Latitude in decimal degrees
    lon: float  # Longitude in decimal degrees
    elevation: Optional[float] = None  # Meters above sea level


@dataclass
class SpeedLimit:
    """Speed limit advisory"""
    type: str = "vehicleMaxSpeed"  # Speed limit type
    speed: int = 60  # Speed in km/h


@dataclass
class WorkZoneDetails:
    """Work zone specific information"""
    risk_score: int  # 1-10 risk score
    workers: int  # Number of workers present
    vehicles: int  # Number of work vehicles
    distance_to_zone: int  # Distance in meters
    hazards: List[str]  # List of identified hazards
    violations: List[str]  # MTO BOOK 7 violations


@dataclass
class AdvisoryItem:
    """Single advisory item in TIM message"""
    item: str  # Advisory type (e.g., "WORK_ZONE_AHEAD")
    speed_limit: Optional[SpeedLimit] = None


class J2735MessageEncoder:
    """
    SAE J2735 message encoder for vRSU broadcast

    Generates valid SAE J2735 messages compatible with:
    - DSRC (Dedicated Short-Range Communications)
    - C-V2X (Cellular Vehicle-to-Everything)
    - V2X-Hub message distribution
    """

    def __init__(self):
        self.msg_counter = 0

    def encode_tim_message(
        self,
        position: Position,
        work_zone: WorkZoneDetails,
        priority: str = "MEDIUM"
    ) -> Dict:
        """
        Generate TIM (Traveler Information Message) for work zone

        Args:
            position: GPS location of work zone
            work_zone: Work zone details from AI analysis
            priority: Message priority (LOW, MEDIUM, HIGH, CRITICAL)

        Returns:
            SAE J2735 TIM message (JSON format)
        """
        self.msg_counter += 1

        # Determine advisory type based on risk score
        if work_zone.risk_score >= 9:
            advisory_type = "CRITICAL_WORK_ZONE_HAZARD"
            speed = 40
        elif work_zone.risk_score >= 7:
            advisory_type = "WORK_ZONE_HAZARD_DETECTED"
            speed = 60
        elif work_zone.risk_score >= 5:
            advisory_type = "WORK_ZONE_AHEAD"
            speed = 60
        else:
            advisory_type = "WORK_ZONE_ACTIVE"
            speed = 80

        message = {
            # Message header (SAE J2735 standard fields)
            "msgID": "TravelerInformation",
            "msgCnt": self.msg_counter % 128,  # Message counter (0-127)
            "timeStamp": self._get_timestamp(),
            "packetID": str(uuid.uuid4()),
            "urlB": "qew.ovin.ca",

            # Data frames (contains actual message content)
            "dataFrames": [{
                "sspTimRights": 0,  # Security permissions
                "frameType": {
                    "type": "workZone",
                    "priority": priority
                },

                # Message ID with position
                "msgId": {
                    "roadSignID": {
                        "position": {
                            "lat": self._encode_lat(position.lat),
                            "lon": self._encode_lon(position.lon),
                            "elevation": position.elevation
                        },
                        "viewAngle": "0000000000000000"  # All directions
                    }
                },

                # Message content
                "startTime": self._get_timestamp(),
                "durationTime": 3600,  # Valid for 1 hour (seconds)

                "content": {
                    # Advisory items
                    "advisory": [
                        {
                            "item": advisory_type,
                            "speed_limit": {
                                "type": "vehicleMaxSpeed",
                                "speed": speed
                            }
                        }
                    ],

                    # Work zone specific data
                    "workZone": {
                        "riskScore": work_zone.risk_score,
                        "workers": work_zone.workers,
                        "vehicles": work_zone.vehicles,
                        "distanceToZone": work_zone.distance_to_zone,
                        "hazards": work_zone.hazards[:3],  # Max 3 hazards
                        "violations": work_zone.violations[:3]  # Max 3 violations
                    }
                },

                # Geographic region affected (circular region)
                "regions": [{
                    "name": "QEW Work Zone Alert",
                    "id": {
                        "region": 0,
                        "id": work_zone.risk_score
                    },
                    "anchor": {
                        "lat": self._encode_lat(position.lat),
                        "lon": self._encode_lon(position.lon)
                    },
                    "laneWidth": 375,  # 3.75m standard lane width (cm)
                    "directionality": 3,  # Both directions
                    "closedPath": False,
                    "direction": "0000000000000000",  # All directions
                    "circle": {
                        "center": {
                            "lat": self._encode_lat(position.lat),
                            "lon": self._encode_lon(position.lon)
                        },
                        "radius": 1000,  # 1km radius (meters)
                        "units": "meter"
                    }
                }]
            }]
        }

        return message

    def encode_rsa_message(
        self,
        position: Position,
        work_zone: WorkZoneDetails,
        alert_type: str = "workZoneHazard"
    ) -> Dict:
        """
        Generate RSA (Road Side Alert) for critical work zone hazards

        Args:
            position: GPS location of hazard
            work_zone: Work zone details from AI analysis
            alert_type: Type of alert (workZoneHazard, etc.)

        Returns:
            SAE J2735 RSA message (JSON format)
        """
        self.msg_counter += 1

        # Determine urgency based on risk score
        if work_zone.risk_score >= 9:
            urgency = "immediate"
            priority = "CRITICAL"
        elif work_zone.risk_score >= 7:
            urgency = "normal"
            priority = "HIGH"
        else:
            urgency = "normal"
            priority = "MEDIUM"

        message = {
            # Message header
            "msgID": "RoadSideAlert",
            "msgCnt": self.msg_counter % 128,
            "timeStamp": self._get_timestamp(),

            # Alert details
            "typeEvent": alert_type,
            "description": {
                "choice": "iti",
                "iti": {
                    "itis": [
                        1799,  # Road work ahead
                        776 if work_zone.workers > 0 else 0,  # Workers present
                    ]
                }
            },

            "priority": priority,
            "urgency": urgency,

            # Hazard position
            "position": {
                "lat": self._encode_lat(position.lat),
                "lon": self._encode_lon(position.lon),
                "elevation": position.elevation
            },

            # Additional details
            "heading": "0000000000000000",  # Unknown heading
            "extent": work_zone.risk_score,  # Use risk score as extent

            # Custom extension with work zone data
            "regional": [{
                "riskScore": work_zone.risk_score,
                "workers": work_zone.workers,
                "hazards": work_zone.hazards[:5],
                "distanceToZone": work_zone.distance_to_zone
            }]
        }

        return message

    def _encode_lat(self, lat: float) -> int:
        """
        Encode latitude to SAE J2735 format (1/10 micro degree)

        Range: -90.0 to +90.0 degrees
        Resolution: 1e-7 degrees
        """
        return int(lat * 10000000)

    def _encode_lon(self, lon: float) -> int:
        """
        Encode longitude to SAE J2735 format (1/10 micro degree)

        Range: -180.0 to +180.0 degrees
        Resolution: 1e-7 degrees
        """
        return int(lon * 10000000)

    def _get_timestamp(self) -> int:
        """
        Get current timestamp in SAE J2735 format

        DDateTime format: minutes since epoch + milliseconds within minute
        """
        now = datetime.now(timezone.utc)
        epoch = datetime(2004, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # Minutes since epoch (2004-01-01 00:00:00 UTC)
        minutes_since_epoch = int((now - epoch).total_seconds() / 60)

        # Milliseconds within current minute
        milliseconds = (now.second * 1000) + (now.microsecond // 1000)

        return {
            "minute": minutes_since_epoch,
            "second": milliseconds
        }

    def validate_message(self, message: Dict) -> bool:
        """
        Validate SAE J2735 message structure

        Args:
            message: Generated message

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "msgID" not in message:
            return False

        if message["msgID"] == "TravelerInformation":
            return "dataFrames" in message and len(message["dataFrames"]) > 0

        elif message["msgID"] == "RoadSideAlert":
            return "position" in message and "typeEvent" in message

        return False

    def get_message_size(self, message: Dict) -> int:
        """
        Get estimated message size in bytes (JSON encoding)

        SAE J2735 recommends messages < 1400 bytes for reliable transmission
        """
        return len(json.dumps(message, separators=(',', ':')))


# Example usage and testing
if __name__ == "__main__":
    encoder = J2735MessageEncoder()

    # Example work zone position (QEW @ Burloak Drive)
    position = Position(lat=43.3850, lon=-79.7400, elevation=80.0)

    # Example work zone from Gemini AI analysis
    work_zone = WorkZoneDetails(
        risk_score=8,
        workers=4,
        vehicles=2,
        distance_to_zone=500,
        hazards=[
            "Workers within 2m of active traffic lane",
            "Approaching vehicle speed >80 km/h",
            "Missing advance warning signage"
        ],
        violations=[
            "BOOK 7 Section 3.2: Insufficient safety measures",
            "BOOK 7 Section 4.1: Missing or inadequate barriers"
        ]
    )

    # Generate TIM message
    tim_message = encoder.encode_tim_message(position, work_zone, priority="HIGH")
    print("=== TIM (Traveler Information Message) ===")
    print(json.dumps(tim_message, indent=2))
    print(f"\nMessage Size: {encoder.get_message_size(tim_message)} bytes")
    print(f"Valid: {encoder.validate_message(tim_message)}")

    print("\n" + "="*60 + "\n")

    # Generate RSA message
    rsa_message = encoder.encode_rsa_message(position, work_zone)
    print("=== RSA (Road Side Alert) ===")
    print(json.dumps(rsa_message, indent=2))
    print(f"\nMessage Size: {encoder.get_message_size(rsa_message)} bytes")
    print(f"Valid: {encoder.validate_message(rsa_message)}")
