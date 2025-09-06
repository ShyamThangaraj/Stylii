import requests
import json
from typing import Dict, Any, Optional

class DesignCritic:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def critique_design(self, room_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Step 2: Apply interior design fundamentals to critique the room
        Uses chain-of-thought reasoning to identify issues and opportunities
        """
        try:
            prompt = f"""
            Based on this room analysis, apply interior design fundamentals to critique the space.
            
            Room Analysis:
            {json.dumps(room_analysis, indent=2)}
            
            Apply these interior design principles in your critique:
            
            1. BALANCE - Visual weight distribution
            2. PROPORTION & SCALE - Relationship between objects and space
            3. RHYTHM - Repetition of colors, patterns, textures, forms
            4. EMPHASIS - Focal points and visual hierarchy
            5. HARMONY & UNITY - Cohesive style and color palette
            6. FUNCTIONALITY - Space efficiency and practical use
            7. LIGHTING - Natural and artificial light optimization
            8. FLOW - Traffic patterns and space navigation
            
            Use chain-of-thought reasoning to:
            1. Assess what's working well
            2. Identify specific problems using design principles
            3. Prioritize the most impactful improvements
            4. Suggest design solutions
            
            Respond with JSON containing:
            {{
                "strengths": ["array of what's working well"],
                "balance_issues": "string - balance problems",
                "proportion_issues": "string - scale/proportion problems", 
                "rhythm_issues": "string - repetition/pattern problems",
                "emphasis_issues": "string - focal point problems",
                "harmony_issues": "string - style cohesion problems",
                "functionality_issues": "string - practical use problems",
                "lighting_issues": "string - lighting problems",
                "flow_issues": "string - traffic flow problems",
                "priority_improvements": ["array of top 3-5 improvements needed"],
                "overall_assessment": "string - summary of main issues and potential"
            }}
            
            Only respond with valid JSON, no additional text.
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
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
            
            critique_result = json.loads(gemini_text.strip())
            return critique_result
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API for design critique: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing design critique response: {e}")
            return None
        except Exception as e:
            print(f"Error generating design critique: {str(e)}")
            return None
    
    def format_critique(self, critique: Dict[str, Any]) -> str:
        """Format critique results for display"""
        if not critique:
            return "No design critique available."
        
        formatted = f"""
DESIGN CRITIQUE:
================

STRENGTHS:
{chr(10).join(['• ' + strength for strength in critique.get('strengths', [])])}

DESIGN ISSUES IDENTIFIED:

Balance: {critique.get('balance_issues', 'No issues identified')}

Proportion & Scale: {critique.get('proportion_issues', 'No issues identified')}

Rhythm: {critique.get('rhythm_issues', 'No issues identified')}

Emphasis: {critique.get('emphasis_issues', 'No issues identified')}

Harmony & Unity: {critique.get('harmony_issues', 'No issues identified')}

Functionality: {critique.get('functionality_issues', 'No issues identified')}

Lighting: {critique.get('lighting_issues', 'No issues identified')}

Flow: {critique.get('flow_issues', 'No issues identified')}

PRIORITY IMPROVEMENTS:
{chr(10).join(['• ' + improvement for improvement in critique.get('priority_improvements', [])])}

OVERALL ASSESSMENT:
{critique.get('overall_assessment', 'No assessment available')}
"""
        return formatted
