import re
import requests
import json
from typing import Dict, Any, Optional

class InputParser:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def parse_user_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Step 3: Parse unstructured user input for budget and preferences
        """
        try:
            prompt = f"""
            Parse this unstructured user input to extract budget and design preferences:
            
            User Input: "{user_input}"
            
            Extract the following information:
            1. Budget amount (look for numbers with currency symbols or words like "budget", "spend", "dollars")
            2. Style preferences (modern, traditional, minimalist, bohemian, scandinavian, industrial, etc.)
            3. Specific needs (storage, lighting, seating, plants, color changes, etc.)
            4. Room constraints (small space, rental restrictions, pet-friendly, etc.)
            5. Color preferences (specific colors mentioned)
            6. Dislikes or things to avoid
            
            Respond with JSON containing:
            """ + """{
                "budget_amount": number or null,
                "budget_currency": "string like USD, EUR" or null,
                "style_preferences": ["array of mentioned styles"],
                "specific_needs": ["array of specific requirements"],
                "room_constraints": ["array of limitations"],
                "color_preferences": ["array of colors mentioned"],
                "dislikes": ["array of things to avoid"],
                "urgency": "string - any timing mentions",
                "parsed_successfully": boolean
            }
            
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
            
            parsed_result = json.loads(gemini_text.strip())
            
            # Add fallback budget extraction if Gemini missed it
            if not parsed_result.get('budget_amount'):
                fallback_budget = self._extract_budget_fallback(user_input)
                if fallback_budget:
                    parsed_result['budget_amount'] = fallback_budget
                    parsed_result['budget_currency'] = 'USD'
            
            return parsed_result
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API for input parsing: {e}")
            return self._fallback_parse(user_input)
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing input response: {e}")
            return self._fallback_parse(user_input)
        except Exception as e:
            print(f"Error parsing user input: {e}")
            return self._fallback_parse(user_input)
    
    def _extract_budget_fallback(self, text: str) -> Optional[float]:
        """Fallback regex-based budget extraction"""
        # Look for patterns like: $500, 500 dollars, budget 500, spend 500
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $500, $1,000
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|bucks?|USD)',  # 500 dollars
            r'budget\s+(?:of\s+)?(?:\$)?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # budget 500
            r'spend\s+(?:up\s+to\s+)?(?:\$)?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # spend 500
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """Simple fallback parsing when API fails"""
        budget = self._extract_budget_fallback(user_input)
        
        # Simple keyword detection for common styles and needs
        styles = []
        needs = []
        colors = []
        
        style_keywords = {
            'modern': 'modern', 'contemporary': 'contemporary',
            'minimalist': 'minimalist', 'scandinavian': 'scandinavian',
            'bohemian': 'bohemian', 'boho': 'bohemian',
            'industrial': 'industrial', 'rustic': 'rustic',
            'traditional': 'traditional', 'classic': 'classic'
        }
        
        need_keywords = {
            'storage': 'storage', 'lighting': 'lighting',
            'seating': 'seating', 'plants': 'plants',
            'shelves': 'storage', 'lamps': 'lighting',
            'chairs': 'seating', 'table': 'furniture'
        }
        
        color_keywords = [
            'white', 'black', 'gray', 'grey', 'blue', 'green',
            'red', 'yellow', 'brown', 'beige', 'navy', 'cream'
        ]
        
        lower_input = user_input.lower()
        
        for keyword, style in style_keywords.items():
            if keyword in lower_input:
                styles.append(style)
        
        for keyword, need in need_keywords.items():
            if keyword in lower_input:
                needs.append(need)
        
        for color in color_keywords:
            if color in lower_input:
                colors.append(color)
        
        return {
            'budget_amount': budget,
            'budget_currency': 'USD' if budget else None,
            'style_preferences': list(set(styles)),
            'specific_needs': list(set(needs)),
            'room_constraints': [],
            'color_preferences': colors,
            'dislikes': [],
            'urgency': None,
            'parsed_successfully': budget is not None or len(styles) > 0 or len(needs) > 0
        }
    
    def format_parsed_input(self, parsed_input: Dict[str, Any]) -> str:
        """Format parsed input for display"""
        if not parsed_input:
            return "No user input parsed."
        
        budget_text = "Not specified"
        if parsed_input.get('budget_amount'):
            currency = parsed_input.get('budget_currency', 'USD')
            budget_text = f"{currency} {parsed_input['budget_amount']:,.2f}"
        
        formatted = f"""
USER PREFERENCES:
=================
Budget: {budget_text}
Style Preferences: {', '.join(parsed_input.get('style_preferences', [])) or 'None specified'}
Specific Needs: {', '.join(parsed_input.get('specific_needs', [])) or 'None specified'}
Color Preferences: {', '.join(parsed_input.get('color_preferences', [])) or 'None specified'}
Room Constraints: {', '.join(parsed_input.get('room_constraints', [])) or 'None specified'}
Dislikes: {', '.join(parsed_input.get('dislikes', [])) or 'None specified'}
"""
        
        if parsed_input.get('urgency'):
            formatted += f"Timing: {parsed_input['urgency']}\n"
        
        return formatted
