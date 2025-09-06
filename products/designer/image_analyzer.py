import base64
import requests
import json
from typing import Dict, Any, Optional

class ImageAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 for Gemini API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Error encoding image: {e}")
    
    def analyze_room_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Step 1: Analyze room image for objects, placement, layout, colors, style
        """
        try:
            # Encode image
            image_base64 = self.encode_image(image_path)
            
            prompt = """
            Analyze this interior room image in detail. I need you to examine:

            1. ROOM TYPE & DIMENSIONS
            - What type of room is this? (living room, bedroom, kitchen, etc.)
            - Approximate size and layout (small/medium/large, layout description)

            2. EXISTING FURNITURE & OBJECTS
            - List all furniture pieces visible
            - Describe their placement and arrangement
            - Note any decorative items, artwork, plants

            3. COLOR SCHEME & LIGHTING
            - Dominant colors in the room
            - Lighting conditions (natural/artificial, bright/dim)
            - Window placement and size

            4. CURRENT STYLE
            - What design style does this room represent?
            - Overall aesthetic impression

            5. SPATIAL ANALYSIS
            - Traffic flow and space utilization
            - Storage visible or lacking
            - Clutter level and organization

            Please respond with a JSON object containing:
            {
                "room_type": "string",
                "size_estimate": "string",
                "furniture_list": ["array of furniture items"],
                "color_palette": ["array of dominant colors"],
                "lighting_assessment": "string description",
                "current_style": "string",
                "spatial_notes": "string about space usage",
                "key_observations": ["array of important details"]
            }

            Only respond with valid JSON, no additional text.
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            gemini_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up response and parse JSON
            gemini_text = gemini_text.strip()
            if gemini_text.startswith('```json'):
                gemini_text = gemini_text[7:]
            if gemini_text.endswith('```'):
                gemini_text = gemini_text[:-3]
            
            analysis_result = json.loads(gemini_text.strip())
            return analysis_result
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini Vision API: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Gemini response: {e}")
            return None
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None
    
    def format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis results for display"""
        if not analysis:
            return "No analysis available."
        
        formatted = f"""
ROOM ANALYSIS:
==============
Room Type: {analysis.get('room_type', 'Unknown')}
Size: {analysis.get('size_estimate', 'Unknown')}
Current Style: {analysis.get('current_style', 'Unknown')}

FURNITURE & OBJECTS:
{', '.join(analysis.get('furniture_list', []))}

COLOR PALETTE:
{', '.join(analysis.get('color_palette', []))}

LIGHTING:
{analysis.get('lighting_assessment', 'No assessment')}

SPATIAL NOTES:
{analysis.get('spatial_notes', 'No notes')}

KEY OBSERVATIONS:
{chr(10).join(['• ' + obs for obs in analysis.get('key_observations', [])])}
"""
        return formatted
