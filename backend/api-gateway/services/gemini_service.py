"""
Gemini Vision API Service
==========================

Integration with Google's Gemini Vision API for work zone detection
and safety analysis from camera images.
"""

import logging
from typing import Dict, Any, Optional, List
import base64
import asyncio
from datetime import datetime

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("google-generativeai not installed. Gemini features disabled.")

from config import settings

logger = logging.getLogger(__name__)


# Configure Gemini API
if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    logger.info(f"✅ Gemini API configured with model: {settings.GEMINI_MODEL}")
else:
    logger.warning("⚠️  Gemini API not configured - using mock responses")


# Work zone analysis prompt
WORK_ZONE_ANALYSIS_PROMPT = """
Analyze this traffic camera image for highway work zone activity and safety compliance.

Identify the following:
1. **Work Zone Presence**: Is there an active work zone visible? (yes/no)
2. **Risk Assessment**: Rate the risk level from 1-10 based on:
   - Number of workers present
   - Proximity to traffic
   - Equipment in use
   - Safety barriers/signage
   - Traffic speed/volume
   - Weather/visibility conditions

3. **Work Zone Elements**:
   - Workers: Count of workers visible
   - Vehicles: Count of work vehicles (trucks, equipment)
   - Equipment: Heavy machinery, trailers, etc.
   - Barriers: Presence of cones, barriers, signs
   - Lane Closures: Number of lanes affected

4. **Hazards**: List specific safety hazards observed:
   - Workers near live traffic
   - Inadequate barriers
   - Poor visibility
   - Equipment blocking lanes
   - Missing signage

5. **MTO BOOK 7 Compliance**: Check Ontario highway work zone standards:
   - Advance warning signage (500m, 200m, 100m)
   - Traffic control devices properly placed
   - Worker safety equipment (high-vis, helmets)
   - Buffer space between workers and traffic
   - Speed reduction signage

6. **Recommendations**: Suggest immediate safety improvements if violations found.

Respond in JSON format:
{
  "has_work_zone": boolean,
  "risk_score": number (1-10),
  "confidence": number (0.0-1.0),
  "workers": number,
  "vehicles": number,
  "equipment": number,
  "barriers": boolean,
  "lane_closures": number,
  "hazards": ["list", "of", "hazards"],
  "violations": ["list", "of", "MTO BOOK 7 violations"],
  "recommendations": ["list", "of", "safety recommendations"],
  "mto_book_compliance": boolean,
  "analysis_text": "brief narrative of findings"
}
"""


class GeminiVisionService:
    """Service for Gemini Vision API work zone analysis"""

    def __init__(self):
        """Initialize Gemini Vision service"""
        self.model_name = settings.GEMINI_MODEL
        self.api_available = GEMINI_AVAILABLE and bool(settings.GEMINI_API_KEY)

        if self.api_available:
            try:
                self.model = genai.GenerativeModel(self.model_name)
                logger.info(f"✅ Gemini model initialized: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini model: {e}")
                self.api_available = False

    async def analyze_work_zone(
        self,
        image_data: str,
        image_type: str = "url",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze camera image for work zone detection

        Args:
            image_data: Image URL or base64-encoded data
            image_type: Either "url" or "base64"
            custom_prompt: Optional custom analysis prompt

        Returns:
            Work zone analysis results
        """
        if not self.api_available:
            logger.warning("Gemini API not available - returning mock response")
            return self._mock_analysis()

        try:
            # Prepare prompt
            prompt = custom_prompt or WORK_ZONE_ANALYSIS_PROMPT

            # Prepare image content
            if image_type == "base64":
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
            elif image_type == "url":
                # Use URL directly (Gemini can fetch URLs)
                image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
            else:
                raise ValueError(f"Invalid image_type: {image_type}")

            # Generate response
            logger.info(f"Calling Gemini Vision API: {self.model_name}")
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, *image_parts]
            )

            # Parse JSON response
            analysis_text = response.text.strip()

            # Try to parse JSON
            import json
            try:
                # Remove markdown code blocks if present
                if analysis_text.startswith("```json"):
                    analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
                elif analysis_text.startswith("```"):
                    analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

                result = json.loads(analysis_text)
                logger.info(f"✅ Gemini analysis complete: work_zone={result.get('has_work_zone')}, risk={result.get('risk_score')}")
                return result

            except json.JSONDecodeError:
                # Fallback: extract key info from text
                logger.warning("Failed to parse Gemini response as JSON, using text analysis")
                return self._parse_text_response(analysis_text)

        except Exception as e:
            logger.error(f"❌ Gemini Vision API error: {e}", exc_info=True)
            return self._error_response(str(e))

    async def batch_analyze(
        self,
        images: List[Dict[str, str]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple images in parallel

        Args:
            images: List of dicts with 'data' and 'type' keys
            max_concurrent: Maximum concurrent API calls

        Returns:
            List of analysis results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_with_limit(image_info):
            async with semaphore:
                return await self.analyze_work_zone(
                    image_info['data'],
                    image_info['type']
                )

        tasks = [analyze_with_limit(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Image {i} analysis failed: {result}")
                processed_results.append(self._error_response(str(result)))
            else:
                processed_results.append(result)

        return processed_results

    def _mock_analysis(self) -> Dict[str, Any]:
        """Return mock analysis for testing without API"""
        return {
            "has_work_zone": False,
            "risk_score": 1,
            "confidence": 0.0,
            "workers": 0,
            "vehicles": 0,
            "equipment": 0,
            "barriers": False,
            "lane_closures": 0,
            "hazards": [],
            "violations": [],
            "recommendations": [],
            "mto_book_compliance": True,
            "analysis_text": "[MOCK] Gemini API not configured. Set GEMINI_API_KEY in .env"
        }

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Return error response structure"""
        return {
            "has_work_zone": False,
            "risk_score": 0,
            "confidence": 0.0,
            "workers": 0,
            "vehicles": 0,
            "equipment": 0,
            "barriers": False,
            "lane_closures": 0,
            "hazards": [],
            "violations": [],
            "recommendations": [],
            "mto_book_compliance": False,
            "analysis_text": f"[ERROR] Analysis failed: {error_msg}"
        }

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """
        Parse text response when JSON parsing fails

        This is a fallback for when Gemini returns text instead of JSON.
        """
        # Simple keyword extraction
        has_work_zone = any(word in text.lower() for word in ["work zone", "construction", "workers"])
        risk_keywords = ["high risk", "dangerous", "hazard", "unsafe"]
        risk_score = 7 if any(kw in text.lower() for kw in risk_keywords) else 3

        return {
            "has_work_zone": has_work_zone,
            "risk_score": risk_score,
            "confidence": 0.5,
            "workers": 0,
            "vehicles": 0,
            "equipment": 0,
            "barriers": False,
            "lane_closures": 0,
            "hazards": [],
            "violations": [],
            "recommendations": [],
            "mto_book_compliance": False,
            "analysis_text": text[:500]  # Truncate to 500 chars
        }


# Global service instance
gemini_service = GeminiVisionService()


# Convenience functions
async def analyze_work_zone_image(image_data: str, image_type: str = "url") -> Dict[str, Any]:
    """
    Convenience function for work zone analysis

    Args:
        image_data: Image URL or base64 data
        image_type: "url" or "base64"

    Returns:
        Analysis results
    """
    return await gemini_service.analyze_work_zone(image_data, image_type)


async def batch_analyze_images(images: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convenience function for batch analysis

    Args:
        images: List of image dicts

    Returns:
        List of analysis results
    """
    return await gemini_service.batch_analyze(images)
