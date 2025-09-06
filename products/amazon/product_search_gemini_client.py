import requests
import json

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def extract_search_terms(self, user_specification):
        """
        Use Gemini to extract comprehensive search terms and criteria from user product specifications
        """
        prompt = f"""
        Analyze this product specification and extract search information for Amazon:
        
        User Request: "{user_specification}"
        
        Please respond with a JSON object containing:
        1. "primary_query" - main search keywords based on the user's natural language request (string, required)
        2. "alternative_queries" - alternative search phrases only if clearly beneficial (array of strings, optional)
        3. "max_price" - maximum price only if explicitly mentioned (number or null)
        4. "min_price" - minimum price only if explicitly mentioned (number or null)
        5. "category" - product category only if clearly specified (string or null)
        6. "must_have_features" - essential features only if explicitly mentioned (array of strings, optional)
        7. "preferred_brands" - brand preferences only if mentioned (array of strings, optional)
        8. "excluded_terms" - terms to avoid only if specified (array of strings, optional)
        9. "sort_preference" - sorting preference only if mentioned: "relevance", "price_low", "price_high", "reviews", "newest" (string, optional)
        10. "use_case" - how the product will be used only if clear from context (string or null)
        11. "quality_indicators" - quality expectations only if mentioned (array of strings, optional)
        
        Important guidelines:
        - Keep the primary_query as close as possible to the user's original natural language
        - Preserve price constraints and other details in the primary query for better Amazon results
        - Only extract additional fields if they provide extra value beyond the primary query
        - Amazon's search works best with natural language queries
        
        Example response:
        {{
            "primary_query": "gaming mouse under 30 dollars",
            "alternative_queries": ["budget gaming mouse under $30", "cheap gaming mouse"],
            "max_price": 30,
            "min_price": null,
            "category": null,
            "must_have_features": ["gaming"],
            "preferred_brands": null,
            "excluded_terms": null,
            "sort_preference": "relevance",
            "use_case": "gaming",
            "quality_indicators": null
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
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            gemini_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean up the response and parse JSON
            gemini_text = gemini_text.strip()
            if gemini_text.startswith('```json'):
                gemini_text = gemini_text[7:]
            if gemini_text.endswith('```'):
                gemini_text = gemini_text[:-3]
            
            search_criteria = json.loads(gemini_text.strip())
            return search_criteria
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Gemini API: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing Gemini response: {e}")
            return None
