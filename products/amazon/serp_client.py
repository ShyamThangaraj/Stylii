import requests
import json
import re
from typing import List, Dict, Any, Optional

class SerpApiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        
        # Mapping of sort preferences to SerpApi parameters
        self.sort_mapping = {
            "relevance": "relevanceblender",
            "price_low": "price-asc-rank",
            "price_high": "price-desc-rank", 
            "reviews": "review-rank",
            "newest": "date-desc-rank",
            "best_sellers": "exact-aware-popularity-rank"
        }
    
    def search_amazon_products(self, search_criteria, max_results=10):
        """
        Advanced Amazon product search using multiple strategies and SerpApi parameters
        """
        all_products = []
        
        # Strategy 1: Primary query with keyword search only
        primary_products = self._search_with_keywords(
            search_criteria.get("primary_query", ""), 
            search_criteria, 
            max_results
        )
        all_products.extend(primary_products)
        
        # Strategy 2: Alternative queries if primary didn't yield enough results
        if len(all_products) < max_results and search_criteria.get("alternative_queries"):
            remaining_results = max_results - len(all_products)
            for alt_query in search_criteria.get("alternative_queries", []):
                if remaining_results <= 0:
                    break
                alt_products = self._search_with_keywords(alt_query, search_criteria, remaining_results)
                all_products.extend(alt_products)
                remaining_results = max_results - len(all_products)
        
        # Remove duplicates based on ASIN
        unique_products = self._remove_duplicates(all_products)
        
        # Filter and rank results based on criteria
        filtered_products = self._filter_and_rank_products(unique_products, search_criteria)
        
        return filtered_products[:max_results]
    
    def _search_with_query(self, query: str, search_criteria: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """
        Perform a single search with optimized parameters using fallback strategy
        """
        if not query:
            return []
        
        # Strategy 1: Try with category node (without k parameter)
        products = []
        if search_criteria.get("amazon_node"):
            products = self._search_with_node(query, search_criteria, max_results)
        
        # Strategy 2: Fallback to keyword search if node search failed or didn't yield enough results
        if len(products) < max_results:
            remaining = max_results - len(products)
            keyword_products = self._search_with_keywords(query, search_criteria, remaining)
            
            # Add keyword products that aren't duplicates
            for product in keyword_products:
                if not any(self._is_duplicate_product(product, existing) for existing in products):
                    products.append(product)
                    if len(products) >= max_results:
                        break
        
        return products[:max_results]
    
    def _search_with_node(self, query: str, search_criteria: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """
        Search within a specific Amazon category node (without k parameter)
        """
        # Build parameters for node-based search
        params = {
            "api_key": self.api_key,
            "engine": "amazon",
            "amazon_domain": "amazon.com",
            "device": "desktop",
            "node": search_criteria["amazon_node"]
        }
        
        # Add price filters
        if search_criteria.get("max_price"):
            params["high_price"] = str(search_criteria["max_price"])
        if search_criteria.get("min_price"):
            params["low_price"] = str(search_criteria["min_price"])
        
        # Add sorting preference
        sort_pref = search_criteria.get("sort_preference", "relevance")
        if sort_pref in self.sort_mapping:
            params["s"] = self.sort_mapping[sort_pref]
        
        # Add advanced filters
        rh_filters = self._build_rh_filters(search_criteria)
        if rh_filters:
            params["rh"] = rh_filters
        
        return self._execute_search(params, max_results)
    
    def _search_with_keywords(self, query: str, search_criteria: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
        """
        Search using keywords (without node parameter)
        """
        # Build parameters for keyword-based search
        params = {
            "api_key": self.api_key,
            "engine": "amazon",
            "k": query,
            "amazon_domain": "amazon.com",
            "device": "desktop"
        }
        
        # Add price filters
        if search_criteria.get("max_price"):
            params["high_price"] = str(search_criteria["max_price"])
        if search_criteria.get("min_price"):
            params["low_price"] = str(search_criteria["min_price"])
        
        # Add sorting preference
        sort_pref = search_criteria.get("sort_preference", "relevance")
        if sort_pref in self.sort_mapping:
            params["s"] = self.sort_mapping[sort_pref]
        
        # Add advanced filters
        rh_filters = self._build_rh_filters(search_criteria)
        if rh_filters:
            params["rh"] = rh_filters
        
        return self._execute_search(params, max_results)
    
    def _execute_search(self, params: Dict[str, str], max_results: int) -> List[Dict[str, Any]]:
        """
        Execute the actual search request
        """
        try:
            response = requests.get(self.base_url, params=params)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if "error" in data:
                return []
            
            products = []
            
            # Extract from organic results
            for result in data.get("organic_results", [])[:max_results]:
                product = self._extract_product_info(result)
                if product:
                    products.append(product)
            
            # Also check sponsored products for relevant results
            for result in data.get("sponsored_products", [])[:max(2, max_results//3)]:
                product = self._extract_product_info(result)
                if product:
                    product["is_sponsored"] = True
                    products.append(product)
            
            return products
            
        except requests.exceptions.RequestException as e:
            return []
        except (KeyError, json.JSONDecodeError) as e:
            return []
    
    def _is_duplicate_product(self, product1: Dict[str, Any], product2: Dict[str, Any]) -> bool:
        """
        Check if two products are duplicates
        """
        # Check ASIN first
        asin1 = product1.get("asin")
        asin2 = product2.get("asin")
        if asin1 and asin2 and asin1 != "N/A" and asin2 != "N/A":
            return asin1 == asin2
        
        # Fallback to title similarity
        title1 = product1.get("title", "")
        title2 = product2.get("title", "")
        return self._calculate_title_similarity(title1, title2) > 0.8
    
    def _build_rh_filters(self, search_criteria: Dict[str, Any]) -> Optional[str]:
        """
        Build advanced rh parameter filters based on search criteria
        """
        filters = []
        
        # Brand filters
        if search_criteria.get("preferred_brands"):
            # This is a simplified example - actual brand codes would need to be mapped
            pass
        
        # Review rating filter (4+ stars)
        quality_indicators = search_criteria.get("quality_indicators") or []
        if "good reviews" in quality_indicators or \
           search_criteria.get("sort_preference") == "reviews":
            filters.append("p_72:1248897011")  # 4+ stars filter
        
        # Prime eligible filter if quality is important
        if any(indicator in ["premium", "quality", "reliable"] 
               for indicator in quality_indicators):
            filters.append("p_85:2470955011")  # Prime eligible
        
        return ",".join(filters) if filters else None
    
    def _extract_product_info(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract and normalize product information from SerpApi result
        """
        try:
            # Extract price information more robustly
            price_raw = result.get("price")
            price_value = None
            if price_raw:
                # Extract numeric price value
                price_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', str(price_raw))
                if price_match:
                    price_value = float(price_match.group(1).replace(',', ''))
            
            # Extract rating as float
            rating_raw = result.get("rating")
            rating_value = None
            if rating_raw:
                rating_match = re.search(r'(\d+(?:\.\d+)?)', str(rating_raw))
                if rating_match:
                    rating_value = float(rating_match.group(1))
            
            # Extract review count
            reviews_raw = result.get("reviews")
            reviews_count = None
            if reviews_raw:
                reviews_match = re.search(r'([\d,]+)', str(reviews_raw))
                if reviews_match:
                    reviews_count = int(reviews_match.group(1).replace(',', ''))
            
            product = {
                "title": result.get("title", "N/A"),
                "asin": result.get("asin", "N/A"),
                "price": price_raw if price_raw else "N/A",
                "price_value": price_value,
                "rating": rating_raw if rating_raw else "N/A",
                "rating_value": rating_value,
                "reviews": reviews_raw if reviews_raw else "N/A",
                "reviews_count": reviews_count,
                "link": result.get("link", "N/A"),
                "thumbnail": result.get("thumbnail", "N/A"),
                "position": result.get("position", "N/A"),
                "is_sponsored": result.get("is_sponsored", False),
                "relevance_score": 0  # Will be calculated later
            }
            
            return product
            
        except Exception as e:
            print(f"Error extracting product info: {e}")
            return None
    
    def _remove_duplicates(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate products based on ASIN
        """
        seen_asins = set()
        unique_products = []
        
        for product in products:
            asin = product.get("asin")
            if asin and asin != "N/A" and asin not in seen_asins:
                seen_asins.add(asin)
                unique_products.append(product)
            elif asin == "N/A":
                # For products without ASIN, check title similarity
                title = product.get("title", "")
                is_duplicate = any(
                    self._calculate_title_similarity(title, existing["title"]) > 0.8
                    for existing in unique_products
                )
                if not is_duplicate:
                    unique_products.append(product)
        
        return unique_products
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two product titles
        """
        if not title1 or not title2:
            return 0.0
        
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _filter_and_rank_products(self, products: List[Dict[str, Any]], search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and rank products based on search criteria
        """
        filtered_products = []
        
        for product in products:
            # Filter by price range
            if self._meets_price_criteria(product, search_criteria):
                # Calculate relevance score
                product["relevance_score"] = self._calculate_relevance_score(product, search_criteria)
                filtered_products.append(product)
        
        # Sort by relevance score (highest first)
        filtered_products.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return filtered_products
    
    def _meets_price_criteria(self, product: Dict[str, Any], search_criteria: Dict[str, Any]) -> bool:
        """
        Check if product meets price criteria
        """
        price_value = product.get("price_value")
        if price_value is None:
            return True  # Include products without clear price info
        
        min_price = search_criteria.get("min_price")
        max_price = search_criteria.get("max_price")
        
        if min_price and price_value < min_price:
            return False
        
        if max_price and price_value > max_price:
            return False
        
        return True
    
    def _calculate_relevance_score(self, product: Dict[str, Any], search_criteria: Dict[str, Any]) -> float:
        """
        Calculate relevance score based on multiple factors
        """
        score = 0.0
        title = product.get("title", "").lower()
        
        # Feature matching (40% of score)
        must_have_features = search_criteria.get("must_have_features", [])
        if must_have_features:
            feature_matches = sum(1 for feature in must_have_features if feature.lower() in title)
            score += (feature_matches / len(must_have_features)) * 40
        
        # Rating score (25% of score)
        rating_value = product.get("rating_value")
        if rating_value:
            score += (rating_value / 5.0) * 25
        
        # Review count factor (15% of score)
        reviews_count = product.get("reviews_count")
        if reviews_count:
            # Normalize review count (log scale)
            import math
            normalized_reviews = min(math.log10(reviews_count + 1) / 4, 1.0)
            score += normalized_reviews * 15
        
        # Brand preference (10% of score)
        preferred_brands = search_criteria.get("preferred_brands", [])
        if preferred_brands:
            brand_matches = sum(1 for brand in preferred_brands if brand.lower() in title)
            score += (brand_matches / len(preferred_brands)) * 10
        
        # Excluded terms penalty (-20 points)
        excluded_terms = search_criteria.get("excluded_terms") or []
        for term in excluded_terms:
            if term.lower() in title:
                score -= 20
        
        # Quality indicators bonus (10% of score)
        quality_indicators = search_criteria.get("quality_indicators") or []
        quality_matches = sum(1 for indicator in quality_indicators if indicator.lower() in title)
        if quality_indicators:
            score += (quality_matches / len(quality_indicators)) * 10
        
        return max(0, score)  # Ensure score is not negative
    
    def format_products(self, products, show_scores=False):
        """
        Format product results for display with enhanced information
        """
        if not products:
            return "No products found."
        
        formatted_output = f"\nFound {len(products)} high-quality products (ranked by relevance):\n"
        formatted_output += "=" * 60 + "\n"
        
        for i, product in enumerate(products, 1):
            # Add relevance indicator
            relevance_score = product.get('relevance_score', 0)
            if relevance_score >= 70:
                relevance_icon = "[HIGH]"  # High relevance
            elif relevance_score >= 50:
                relevance_icon = "[GOOD]"  # Good relevance
            elif relevance_score >= 30:
                relevance_icon = "[MODERATE]"  # Moderate relevance
            else:
                relevance_icon = "[BASIC]"  # Basic match
            
            formatted_output += f"\n{relevance_icon} {i}. {product['title']}\n"
            
            # Price with value indicator
            if product['price'] != "N/A":
                price_text = f"   Price: {product['price']}"
                if product.get('price_value') and product.get('rating_value'):
                    # Add value indicator for good price/rating ratio
                    if product['rating_value'] >= 4.0 and product.get('price_value', 0) < 100:
                        price_text += " [GOOD VALUE]"
                formatted_output += price_text + "\n"
            
            # Enhanced rating display
            if product['rating'] != "N/A":
                rating_text = f"   Rating: {product['rating']}"
                if product['reviews'] != "N/A":
                    rating_text += f" ({product['reviews']} reviews)"
                    # Add popularity indicator for highly reviewed products
                    if product.get('reviews_count', 0) > 1000:
                        rating_text += " [POPULAR]"
                formatted_output += rating_text + "\n"
            
            # Show if it's a sponsored result
            if product.get('is_sponsored'):
                formatted_output += f"   [SPONSORED RESULT]\n"
            
            # Show relevance score in verbose mode
            if show_scores and relevance_score > 0:
                formatted_output += f"   Relevance score: {relevance_score:.1f}/100\n"
            
            if product['asin'] != "N/A":
                formatted_output += f"   ASIN: {product['asin']}\n"
            
            if product['link'] != "N/A":
                formatted_output += f"   Link: {product['link']}\n"

            if product['thumbnail'] != "N/A":
                formatted_output += f"   Thumbnail: {product['thumbnail']}\n"
                
            formatted_output += "-" * 50 + "\n"
        
        return formatted_output
