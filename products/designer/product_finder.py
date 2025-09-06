import sys
import os
import requests
import json
from typing import Dict, Any, List, Optional

# Add the parent directory to the path to import from amazon module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amazon.product_search_gemini_client import GeminiClient
from amazon.serp_client import SerpApiClient

class ProductFinder:
    def __init__(self, gemini_api_key: str, serpapi_key: str):
        self.gemini_api_key = gemini_api_key
        self.serpapi_key = serpapi_key
        self.gemini_client = GeminiClient(gemini_api_key)
        self.serp_client = SerpApiClient(serpapi_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def generate_product_recommendations(self, room_analysis: Dict[str, Any], 
                                       design_critique: Dict[str, Any], 
                                       user_preferences: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Step 4: Generate specific product recommendations based on all analysis
        """
        try:
            # First, use Gemini to generate specific product searches based on analysis
            product_searches = self._generate_product_searches(room_analysis, design_critique, user_preferences)
            
            if not product_searches:
                return None
            
            # Then search for each product category
            all_products = []
            budget = user_preferences.get('budget_amount', 1000)
            
            for search_info in product_searches:
                products = self._search_products(search_info, budget)
                if products:
                    # Add category info to products
                    for product in products[:1]:  # Limit to top 1 per category
                        product['category'] = search_info.get('category', 'General')
                        product['reasoning'] = search_info.get('reasoning', '')
                        all_products.append(product)
            
            # Sort by relevance and budget fit
            sorted_products = self._prioritize_products(all_products, budget)
            
            return sorted_products
            
        except Exception as e:
            print(f"Error generating product recommendations: {e}")
            return None
    
    def _generate_product_searches(self, room_analysis: Dict[str, Any], 
                                 design_critique: Dict[str, Any], 
                                 user_preferences: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Generate specific product search queries based on analysis"""
        try:
            prompt = f"""
            Based on this room analysis, design critique, and user preferences, generate specific product search queries for Amazon.
            
            Room Analysis:
            {json.dumps(room_analysis, indent=2)}
            
            Design Critique:
            {json.dumps(design_critique, indent=2)}
            
            User Preferences:
            {json.dumps(user_preferences, indent=2)}
            
            Generate 4-8 specific product searches that address the priority improvements identified.
            Focus on products that will have the most impact within the user's budget.
            
            For each product search, provide:
            1. Specific search query for Amazon
            2. Category (lighting, furniture, decor, storage, etc.)
            3. Price range suggestion
            4. Reasoning why this product addresses the design issues
            
            Respond with JSON array:
            [
                {{
                    "search_query": "modern floor lamp with warm light",
                    "category": "lighting",
                    "price_range_max": 150,
                    "reasoning": "Addresses lighting issues identified in critique"
                }}
            ]
            
            Only respond with valid JSON array, no additional text.
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
                'X-goog-api-key': self.gemini_api_key
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
            
            searches = json.loads(gemini_text.strip())
            return searches
            
        except Exception as e:
            print(f"Error generating product searches: {e}")
            return self._fallback_searches(design_critique, user_preferences)
    
    def _fallback_searches(self, design_critique: Dict[str, Any], 
                          user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback product searches when AI generation fails"""
        searches = []
        
        # Basic searches based on common needs
        if 'lighting' in str(design_critique).lower():
            searches.append({
                "search_query": "modern table lamp",
                "category": "lighting",
                "price_range_max": 100,
                "reasoning": "Improve lighting issues"
            })
        
        if 'storage' in str(design_critique).lower():
            searches.append({
                "search_query": "storage shelves",
                "category": "storage", 
                "price_range_max": 150,
                "reasoning": "Add storage solutions"
            })
        
        # Add searches based on user needs
        for need in user_preferences.get('specific_needs', []):
            if need == 'plants':
                searches.append({
                    "search_query": "indoor plants large",
                    "category": "decor",
                    "price_range_max": 50,
                    "reasoning": "User requested plants"
                })
        
        return searches
    
    def _search_products(self, search_info: Dict[str, Any], total_budget: float) -> List[Dict[str, Any]]:
        """Search for products using existing Amazon search infrastructure"""
        try:
            # Use existing Gemini client to extract search criteria
            search_criteria = self.gemini_client.extract_search_terms(search_info['search_query'])
            
            if not search_criteria:
                return []
            
            # Add budget constraint
            max_price = min(search_info.get('price_range_max', total_budget * 0.3), total_budget * 0.4)
            search_criteria['max_price'] = max_price
            
            # Search using existing SerpApi client
            products = self.serp_client.search_amazon_products(search_criteria, max_results=3)
            
            return products
            
        except Exception as e:
            print(f"Error searching products for {search_info.get('search_query', 'unknown')}: {e}")
            return []
    
    def _prioritize_products(self, products: List[Dict[str, Any]], budget: float) -> List[Dict[str, Any]]:
        """Prioritize products based on budget fit and impact"""
        if not products:
            return []
        
        # Calculate running total and prioritize
        prioritized = []
        running_total = 0
        
        # Sort by category importance and price
        category_priority = {
            'lighting': 1,
            'storage': 2, 
            'furniture': 3,
            'decor': 4
        }
        
        products.sort(key=lambda p: (
            category_priority.get(p.get('category', 'decor'), 5),
            p.get('price_value', 999999) if p.get('price_value') is not None else 999999
        ))
        
        for product in products:
            price = product.get('price_value', 0)
            if price and isinstance(price, (int, float)) and running_total + price <= budget:
                prioritized.append(product)
                running_total += price
            elif not price or price is None:  # Include products without clear price
                prioritized.append(product)
        
        return prioritized
    
    def format_recommendations(self, products: List[Dict[str, Any]], 
                             user_preferences: Dict[str, Any]) -> str:
        """Format product recommendations for display"""
        if not products:
            return "No product recommendations available."
        
        budget = user_preferences.get('budget_amount', 0)
        currency = user_preferences.get('budget_currency', 'USD')
        
        total_cost = sum(p.get('price_value', 0) for p in products if p.get('price_value'))
        
        formatted = f"""
PRODUCT RECOMMENDATIONS:
========================
Budget: {currency} {budget:,.2f}
Estimated Total: {currency} {total_cost:,.2f}
Remaining Budget: {currency} {max(0, budget - total_cost):,.2f}

RECOMMENDED PRODUCTS:
"""
        
        for i, product in enumerate(products, 1):
            formatted += f"""
{i}. {product.get('title', 'Product')}
   Category: {product.get('category', 'General')}
   Price: {product.get('price', 'Price not available')}
   Rating: {product.get('rating', 'No rating')} ({product.get('reviews', 'No reviews')})
   Why: {product.get('reasoning', 'Recommended based on analysis')}
   Link: {product.get('link', 'No link available')}
   Thumbnail: {product.get('thumbnail', 'No thumbnail available')}
   ---
"""
        
        return formatted
